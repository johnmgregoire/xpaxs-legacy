import os,sys
path=path=os.path.join(os.path.expanduser("~"),
            "workspace/spectromicroscopy/spectromicroscopy/")

os.system("pyuic4 %s/SMP.ui>%s/SMP.py"%(path,path))
os.system("pyuic4 %s/Xp.ui>%s/Xp.py"%(path,path))
os.system("pyuic4 %s/GearTester.ui>%s/GearTester.py"%(path,path))
from PyQt4 import QtCore, QtGui    
from SMP import Ui_Main
from MotorGui import MyUI
from KonsoleGui import MyKon
from XpGui import MyXP


class MySMP(Ui_Main,QtGui.QMainWindow):
    """Establishes a Experimenbt controls"""
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.Opener=QtGui.QMenu("New",self.Bar)
        self.Opener.addAction("Motor Control",self.NewMotor)
        self.Opener.addAction("Console",self.NewKon)
        self.XP=MyXP(self)
        self.NewMotor()
        self.Tabby.addTab(self.XP.centralWidget(),"Experiment Controls")
        self.NewKon()
        self.Tabby.removeTab(0)
    def NewMotor(self):
        self.Bar.clear()
        self.Bar.addMenu(self.Opener)
        self.Motor=MyUI(self)
        self.Tabby.addTab(self.Motor.centralWidget(),"Motor Controler")
        QtCore.QObject.connect(self.Motor.Closer,QtCore.SIGNAL("clicked()"),\
                                 self.Del)
    def NewKon(self):
        self.Kon=MyKon(self)
        self.Tabby.addTab(self.Kon.centralWidget(),"Console")
        QtCore.QObject.connect(self.Kon.Closer,QtCore.SIGNAL("clicked()"),\
                                 self.Del)
    def Del(self):
        Index=self.Tabby.currentIndex()
        if self.Tabby.tabText(Index)=="Motor Controler":
            self.Motor=None
        elif self.Tabby.tabText(Index)=="Console":
            self.Kon=None
        self.Tabby.removeTab(Index)
        
if __name__ == "__main__":
    print __file__
    app = QtGui.QApplication(sys.argv)
    myapp = MySMP()
    myapp.show()
    sys.exit(app.exec_())
