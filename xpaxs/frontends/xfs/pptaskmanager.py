"""
"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------

import logging
import time

#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

import pp
from PyMca import ClassMcaTheory
from PyMca.ConcentrationsTool import ConcentrationsTool
from PyQt4 import QtCore
import numpy
numpy.seterr(all='ignore')

#---------------------------------------------------------------------------
# xpaxs imports
#---------------------------------------------------------------------------

from xpaxs.dispatch.pptaskmanager import PPTaskManager

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------


logger = logging.getLogger(__file__)
DEBUG = False

def flat_to_nd(index, shape):
    res = []
    for i in xrange(1, len(shape)):
        p = numpy.product(shape[i:])
        res.append(index//p)
        index = index % p
    res.append(index)
    return tuple(res)

def analyzeSpectrum(index, spectrum, tconf, advancedFit, mfTool):
    start = time.time()
    advancedFit.config['fit']['use_limit'] = 1
    # TODO: get the channels from the controller
    advancedFit.setdata(y=spectrum)
    advancedFit.estimate()
    estimate = time.time()
    if ('concentrations' in advancedFit.config) and \
            (advancedFit._fluoRates is None):
        fitresult, result = advancedFit.startfit(digest=1)
    else:
        fitresult = advancedFit.startfit(digest=0)
        result = advancedFit.imagingDigestResult()
    result['index'] = index
    fit = time.time()

    if mfTool:
        temp = {}
        temp['fitresult'] = fitresult
        temp['result'] = result
        temp['result']['config'] = advancedFit.config
        tconf.update(advancedFit.configure()['concentrations'])
        conc = mfTool.processFitResult(config=tconf, fitresult=temp,
                                       elementsfrommatrix=False,
                                       fluorates=advancedFit._fluoRates)
        result['concentrations'] = conc
    fitconc = time.time()
    report = {'estimate':estimate-start,
              'fit': fit-estimate,
              'fitconc': fitconc-fit}

    return {'index': index, 'result': result, 'advancedFit': advancedFit, 'report': report}


class XfsPPTaskManager(PPTaskManager):

    def _submitJobs(self, numJobs):
        try:
            self.mutex.lock()
            for i in range(numJobs):
                try:
                    index, data = self.iterData.next()
                    args = (index, data, self.tconf, self.advancedFit, self.mfTool)
                    self.jobServer.submit(
                        analyzeSpectrum,
                        args,
                        modules=("time", ),
                        callback=self.updateRecords
                    )
                except IndexError:
                    break
        finally:
            self.mutex.unlock()

    def setData(self, scan, config):
        self.scan = scan
        self.iterData = scan.iterMcaSpectra

        self.config = config

        self.advancedFit = ClassMcaTheory.McaTheory(config=config)
        self.advancedFit.enableOptimizedLinearFit()
        self.mfTool = None
        if 'concentrations' in config:
            self.mfTool = ConcentrationsTool(config)
            self.tconf = self.mfTool.configure()

    def updateRecords(self, data):
        if data:
            try:
                self.mutex.lock()
                if DEBUG: print 'Updating records'

                self.advancedFit = data['advancedFit']
                shape = self.scan.scanShape
                index = flat_to_nd(data['index'], shape)

                result = data['result']
                for group in result['groups']:
                    g = group.replace(' ', '')

                    fitArea = result[group]['fitarea']
                    if fitArea: sigmaArea = result[group]['sigmaarea']/fitArea
                    else: sigmaArea = numpy.nan

                    self.scan.updateElementMap('fitArea', g, index, fitArea)
                    self.scan.updateElementMap('sigmaArea', g, index, sigmaArea)

                if 'concentrations' in result:
                    massFractions = result['concentrations']['mass fraction']
                    for key, val in massFractions.iteritems():
                        k = key.replace(' ', '')
                        self.scan.updateElementMap('massFraction', k, index, val)
                self.dirty = True
                self.emit(
                    QtCore.SIGNAL('percentComplete'),
                    (100.0 * self.iterData.currentIndex) / \
                        self.iterData.numExpectedPoints
                )
                if DEBUG: print 'records updated'
            finally:
                self.mutex.unlock()
