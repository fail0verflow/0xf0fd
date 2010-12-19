import sys
import os
import os.path

from PySide import QtCore, QtGui

from idis.datastore import DataStore
from arch.shared_opcode_types import *
from disassemblywidget import DisassemblyWidget
from symbolwidget import SymbolWidget
import arch

class ArchPromptWindow(QtGui.QWidget):
    def __init__(self, callback):
        super(ArchPromptWindow, self).__init__()
        self.resize(500, 200)

        self.callback = callback

        ob = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()
        ob.addLayout(hbox)
        
        controlsBox = QtGui.QVBoxLayout()
        hbox.addLayout(controlsBox)

        # Friendly wizard
        img = QtGui.QPixmap("resources/wizard.png")
        imglabel = QtGui.QLabel()
        imglabel.setPixmap(img)
        hbox.addStretch()
        hbox.addWidget(imglabel)

        # Add text labels
        textlabel = QtGui.QLabel("It looks like you're starting a new database!")
        textlabel2 = QtGui.QLabel("Select an architecture:")
        controlsBox.addWidget(textlabel)
        controlsBox.addWidget(textlabel2)

        # Add arch selection box
        mns = arch.machineNames()
        self.qcb = QtGui.QComboBox()
        for i in mns:
            self.qcb.addItem(arch.machine_list[i].longname, i)
        controlsBox.addWidget(self.qcb)
        controlsBox.addStretch()

        # launch button
        bbox = QtGui.QHBoxLayout()
        okBtn = QtGui.QPushButton("Launch!")
        okBtn.clicked.connect(self.launchClick)
        bbox.addStretch()
        bbox.addWidget(okBtn)

        ob.addLayout(bbox)

        self.setLayout(ob)
        
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.Dialog)

    def launchClick(self):
        self.close()
        self.callback(self.qcb.itemData(self.qcb.currentIndex(), role=QtCore.Qt.UserRole))


class MainWindow(QtGui.QMainWindow):
    def __init__(self, gui, ds, filename):
        super(MainWindow, self).__init__()
        self.gui = gui
        
        self.resize(800,600)
        self.setWindowTitle(filename)
        
        disassemblyWidget = DisassemblyWidget(self, gui, ds)
        symbolWidget = SymbolWidget(self, ds)
        

        symbolWidget.widget.symbolSelected.connect(disassemblyWidget.gotoAddress)

        self.setCentralWidget(disassemblyWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, symbolWidget)

class QTGui(object):
    def __init__(self):
        pass

    def startup(self):
        pass

    def newWithArchCallback(self, arch):
        self.global_archname = arch

        ds = DataStore(self.filename)
        ds.properties.set("f0fd.HACK_arch_name", arch)
        mainWin = MainWindow(self, ds, self.filename)
        mainWin.show()

    def mainloop(self, filenames):
        if (len(filenames) < 1):
            print "usage: idis filename"
            sys.exit(-1)

        self.filename = filenames[0]

        self.app = QtGui.QApplication(sys.argv)

        if not os.path.exists(self.filename):
            apw = ArchPromptWindow(self.newWithArchCallback)
            apw.show()
        else:
            ds = DataStore(self.filename)
            try:
                self.global_archname = ds.properties.get("f0fd.HACK_arch_name")
                mainWin = MainWindow(self, ds, self.filename)
                mainWin.show()

            except KeyError:
                # Hack to set primary architecture for databases that don't have one
                def runShowCallBack(arch):
                    self.global_archname = arch
                    ds.properties.set("f0fd.HACK_arch_name", arch)
                    mainWin = MainWindow(self, ds, self.filename)
                    mainWin.show()
                
                apw = ArchPromptWindow(runShowCallBack)
                apw.show()

           
        self.app.exec_()


    def shutdown(self):
        pass

    def except_shutdown(self):
        self.app.exit()
