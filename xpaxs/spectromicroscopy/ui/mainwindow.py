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
# xpaxs imports
#---------------------------------------------------------------------------

from xpaxs import configutils
from xpaxs import __version__
from xpaxs.spectromicroscopy.ui import ui_mainwindow

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------


class MainWindow(ui_mainwindow.Ui_MainWindow, QtGui.QMainWindow):
    """Establishes a Experiment controls

    1) establishes week connection to specrunner
    2) creates ScanIO instance with Experiment Controls
    3) Connects Actions from Toolbar

    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        self.mdi = QtGui.QMdiArea()
        self.setCentralWidget(self.mdi)

        self.statusBar.showMessage('Ready', 2000)
        self.progressBar = QtGui.QProgressBar(self.statusBar)
        self.progressBar.hide()

        self.specInterface = None
        self.fileView = None
        self.fileModel = None
        #TODO: added Consoles and motorViews
        self.console = None
        self.motorView = None

        settings = QtCore.QSettings()
        settings.beginGroup('MainWindow')
        self.restoreGeometry(settings.value('Geometry').toByteArray())

        self.connectSignals()

    def connectSignals(self):
        self.connect(self.actionOpen,
                     QtCore.SIGNAL("triggered()"),
                     self.openDatafile)
        self.connect(self.actionConnect,
                     QtCore.SIGNAL("triggered()"),
                     self.connectToSpec)
        self.connect(self.actionDisconnect,
                     QtCore.SIGNAL("triggered()"),
                     self.disconnectFromSpec)
        self.connect(self.actionAbout_Qt,
                     QtCore.SIGNAL("triggered()"),
                     QtGui.qApp,
                     QtCore.SLOT("aboutQt()"))
        self.connect(self.actionAbout_SMP,
                     QtCore.SIGNAL("triggered()"),
                     self.about)
#        self.connect(self.actionSave,
#                     QtCore.SIGNAL("triggered()"),
#                     self.save)
#        self.connect(self.actionSave_All,
#                     QtCore.SIGNAL("triggered()"),
#                     self.saveAll)
#        self.connect(self.actionClose,
#                     QtCore.SIGNAL("triggered()"),
#                     self.closeScan)
#        self.connect(self.actionClose_All,
#                     QtCore.SIGNAL("triggered()"),
#                     self.closeAllScans)

    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About SMP"),
            self.tr("SMP Application, version %s\n\n"
                    "SMP is a user interface for controlling synchrotron "
                    "experiments and analyzing data. SMP is a part of xpaxs "
                    "and depends on several programs and libraries:\n\n"
                    "    spec: for controlling hardware and data acquisition\n"
                    "    SpecClient: a python interface to the spec server\n"
                    "    PyMca: a set of programs and libraries for analyzing "
                    "X-ray fluorescence spectra"%__version__))

    def closeEvent(self, event):
        if self.specInterface: self.specInterface.close()
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue('Geometry', QtCore.QVariant(self.saveGeometry()))
        return event.accept()

#    def closeScan(self):
#        NotImplementedError
#
#    def closeAllScans(self):
#        NotImplementedError
#
#    def open(self):
#        NotImplementedError
#
#    def save(self):
#        raise NotImplementedError
#
#    def saveAll(self):
#        NotImplementedError

    def connectToSpec(self):
        from spectromicroscopy.smpgui import configuresmp
        if not configuresmp.ConfigureSmp(self).exec_(): return
        try:
            from spectromicroscopy.smpgui import specinterface
            from SpecClient import SpecClientError

            self.specInterface = \
                specinterface.SpecInterface(statusBar=self.statusBar)
            self.specDockWidget = QtGui.QDockWidget('spec', self)
            self.specDockWidget.setObjectName('SpecDockWidget')
            self.specDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|
                                                QtCore.Qt.RightDockWidgetArea)
            self.specDockWidget.setWidget(self.specInterface)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                               self.specDockWidget)
            # TODO: add to View menu
        except SpecClientError.SpecClientTimeoutError:
            self.connectToSpec()
        self.actionConnect.setEnabled(False)
        self.actionDisconnect.setEnabled(True)

    def disconnectFromSpec(self):
        self.specDockWidget.close()
        self.actionConnect.setEnabled(True)
        self.actionDisconnect.setEnabled(False)
        # TODO: remove from View menu

    def showProgressBar(self):
        self.statusBar.addWidget(self.progressBar)
        self.progressBar.show()

    def hideProgressBar(self):
        self.statusBar.removeWidget(self.progressBar)
        self.progressBar.hide()

#    # TODO: This interface needs attention
#    def newMotorView(self):
#        from testinterface import MyUI
#        self.motorView = MyUI(self)
#        self.mainTab.addTab(self.Motor.centralWidget(), "Motor Controler")
#        self.connect(self.Motor.Closer,
#                     QtCore.SIGNAL("clicked()"),
#                     self.Del)
#
#    # TODO: update the console UI, use proper naming convention
#    # Dont make it a main window, no central widget.
#    def newConsole(self):
#        if self.console is None:
#            from spectromicroscopy.smpgui import console
#            self.console = console.MyKon(self)
#        self.mainTab.addTab(self.console.centralWidget(), "Console")
#        self.connect(self.console.Closer,
#                     QtCore.SIGNAL("clicked()"),
#                     self.Del)

    def openDatafile(self):
        f = '%s'% QtGui.QFileDialog.getOpenFileName(self, 'Open File', '.',
                "hdf5 files (*.h5 *.hdf5);;Spec datafiles (*.dat *.mca);;All files (*.*)")
        # TODO: convert specfiles to hdf5
        if not f: return
        if self.fileView is None:
            from xpaxs.datalib.hdf5 import qtdatamodel
            self.fileModel = qtdatamodel.FileModel()
            self.connect(self.fileModel,
                         QtCore.SIGNAL('scanActivated'),
                         self.newScanWindow)
            self.fileView = QtGui.QTreeView()
            self.fileView.setModel(self.fileModel)
            self.fileView.connect(self.fileView,
                                  QtCore.SIGNAL('activated(QModelIndex)'),
                                  self.fileModel.itemActivated)
            self.fileDockWidget = QtGui.QDockWidget('file', self)
            self.fileDockWidget.setObjectName('FileDockWidget')
            self.fileDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|
                                                    QtCore.Qt.RightDockWidgetArea)
            self.fileDockWidget.setWidget(self.fileView)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                               self.fileDockWidget)
        self.fileModel.appendFile(f)
        self.fileView.doItemsLayout()
        row = self.fileModel.rowCount(QtCore.QModelIndex())-1
        index = self.fileModel.index(row, 0, QtCore.QModelIndex())
        self.fileView.expand(index)
        self.fileView.resizeColumnToContents(0)
        self.fileView.resizeColumnToContents(1)
        self.fileView.resizeColumnToContents(2)

    def newScanWindow(self, scan):
        from xpaxs.spectromicroscopy.ui import scananalysis
        from xpaxs.spectromicroscopy import analysisController
        controller = analysisController.AnalysisController(scan)
        scanView = scananalysis.ScanAnalysis(controller)
        self.mdi.addSubWindow(scanView)
        scanView.show()


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    form = SmpMainWindow()
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()