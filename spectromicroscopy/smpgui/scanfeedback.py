"""
"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

#---------------------------------------------------------------------------
# SMP imports
#---------------------------------------------------------------------------

from spectromicroscopy.smpgui import ui_scanfeedback,  scananalysis

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------

class ScanFeedback(ui_scanfeedback.Ui_ScanFeedback, QtGui.QWidget):
    """Establishes a Experimenbt controls    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.scanFeedbackTab.removeTab(0)
        
        self.specRunner = parent.specRunner
        self.scanAnalyses = []
        self.PymcaConfigFile=None
        
        self.connect(self.specRunner.scan, 
                     QtCore.SIGNAL("newMesh(PyQt_PyObject)"),
                     self.newScanAnalysis2D)
        self.connect(self.specRunner.scan,
                     QtCore.SIGNAL("newScan(PyQt_PyObject)"),
                     self.setTabLabel)
        self.connect(self.window(),
                     QtCore.SIGNAL("pymcaConfigFileChanged(PyQt_PyObject)"),
                     self.setPymcaConfigFile)

    def newScanAnalysis1D(self, scanParams):
        newAnalysis = ScanAnalysis1D(self)
        self.scanAnalyses.append(newAnalysis)
        self.scanFeedbackTab.addTab(newAnalysis, '')
        self.scanFeedbackTab.setCurrentWidget(newAnalysis)
        
    def newScanAnalysis2D(self, scanParams):
        newAnalysis = scananalysis.ScanAnalysis2D(self, scanParams)
        self.scanAnalyses.append(newAnalysis)
        self.scanFeedbackTab.addTab(newAnalysis, '')
        self.scanFeedbackTab.setCurrentWidget(newAnalysis)

    def setTabLabel(self, scanParams):
        i = self.scanFeedbackTab.currentIndex()
        self.scanFeedbackTab.setTabText(i, scanParams['title'])
    
    def setPymcaConfigFile(self,filename):
        self.PymcaConfigFile=filename
