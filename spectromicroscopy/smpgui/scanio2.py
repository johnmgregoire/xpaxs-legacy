"""
"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------

import codecs
import os
import sys
import tempfile
import time

#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

import numpy
from PyMca import ClassMcaTheory , ConcentrationsTool 
from PyQt4 import QtCore, QtGui

#---------------------------------------------------------------------------
# SMP imports
#---------------------------------------------------------------------------

from spectromicroscopy.smpgui import configuresmp, ui_scanio2, scancontrols, \
    scanfeedback
#from mplwidgets import MplCanvas
from spectromicroscopy.smpcore import specrunner, configutils

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------

DEBUG = 2 # ??


class ScanIO(ui_scanio2.Ui_ScanIO, QtGui.QWidget):
    """Establishes a Experimenbt controls    """
    def __init__(self, parent=None):
        self.DEBUG=DEBUG
        QtGui.QWidget.__init__(self, parent)
        self.parent=parent
        self.setupUi(self)
        
        # TODO: this is for debugging
        try:
            self.specrunner = parent.specrunner
        except AttributeError:
            # for debugging, run seperately from main smp
            specVersion = self.getSpecVersion()
            self.specrunner = specrunner.SpecRunner(specVersion, timeout=500)
        
        self.scanControls = scancontrols.ScanControls(self)
        self.gridlayout.addWidget(self.scanControls,0,0,1,1)

        self.scanFeedback = scanfeedback.ScanFeedback(self)
        self.gridlayout.addWidget(self.scanFeedback,0,1,1,1)
        
        # TODO: This probably needs to go in the main app window?
        self.timer = QtCore.QTimer(self)
        QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.specrunner.update)
        self.timer.start(20)

    def getSpecVersion(self):
        smpConfig = configutils.getSmpConfig()
        try:
            return ':'.join([smpConfig['session']['server'],
                             smpConfig['session']['port']])
        except KeyError:
            editor = configure.ConfigureSmp(self)
            editor.exec_()
            self.getSpecVersion()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = ScanIO()
    myapp.show()
    sys.exit(app.exec_())