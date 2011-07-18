import sys
import os
import os.path

from PySide import QtCore, QtGui

from datastore import DataStore
from arch.shared_opcode_types import *
from applogic.defaultmockproxy import DefaultMockProxy
import applogic.tools

from mainwindow import MainWindow
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
        textlabel = QtGui.QLabel(
            "It looks like you're starting a new database!")

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
        self.callback(
            self.qcb.itemData(self.qcb.currentIndex(),
                role=QtCore.Qt.UserRole))


class QTGui(object):
    def __init__(self):
        pass

    def startup(self):
        pass

    def createMainWindow(self):
        mainWin = MainWindow(self, self.filename)
        mainWin.show()

    def engineSetupCompletion(self):
        applogic.tools.registerFunctionality(self.ds)

    def newWithArchCallback(self, archname):
        self.global_archname = archname

        self.ds = DataStore(self.filename, applogic.tools.typeFactory)
        self.user_ds = DefaultMockProxy(self.ds)

        self.ds.properties.set("f0fd.HACK_arch_name", archname)
        self.engineSetupCompletion()
        self.createMainWindow()

    def runShowCallBack(self, archname):
        self.global_archname = archname
        self.ds.properties.set("f0fd.HACK_arch_name", archname)
        self.createMainWindow()

    def mainloop(self, filenames):
        if (len(filenames) < 1):
            print "usage: %s filename" % sys.argv[0]
            sys.exit(-1)

        self.filename = filenames[0]

        self.app = QtGui.QApplication(sys.argv)

        if not os.path.exists(self.filename):
            # File doesn't exist, show arch
            # prompt window and create the datastore
            apw = ArchPromptWindow(self.newWithArchCallback)
            apw.show()
        else:
            # File exists, make sure the architecture type is properly set
            self.ds = DataStore(self.filename, applogic.tools.typeFactory)
            self.user_ds = DefaultMockProxy(self.ds)
            try:
                self.global_archname = \
                    self.ds.properties.get("f0fd.HACK_arch_name")

                self.engineSetupCompletion()
                self.createMainWindow()

            except KeyError:
                apw = ArchPromptWindow(self.runShowCallBack)
                apw.show()

        self.app.exec_()

    def shutdown(self):
        pass

    def except_shutdown(self):
        self.app.exit()
