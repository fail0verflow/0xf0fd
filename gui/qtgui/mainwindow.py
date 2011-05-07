from PySide import QtGui, QtCore

from subviewmgr import SubViewManager
from disassemblywidget import DisassemblyWidget

from datastore.dbtypes import CommentPosition

from applogic.cmd import CompoundCommand, SymbolNameCommand, CommentCommand
import applogic.tools_loaders

import json


class AddBinaryPromptWindow(QtGui.QDialog):
    def __init__(self):
        super(AddBinaryPromptWindow, self).__init__()

        # Todo - make validator that changes background red for bad values
        # and disables okButton

        # TODO: add cancel button

        # TODO: remove close and make act like a normal dialog
        okButton = QtGui.QPushButton("OK")
        okButton.setDefault(True)
        QtCore.QObject.connect(okButton,
            QtCore.SIGNAL('clicked()'), self.accept)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtGui.QDialogButtonBox.ActionRole)

        self.formLayout = QtGui.QFormLayout()
        self.baseEdit = QtGui.QLineEdit("0x0")
        self.startEdit = QtGui.QLineEdit("0x0")
        self.lengthEdit = QtGui.QLineEdit("-1")
        self.formLayout.addRow("&Base Address:", self.baseEdit)
        self.formLayout.addRow("&Start Offset:", self.startEdit)
        self.formLayout.addRow("&Length:", self.lengthEdit)
        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, gui, filename):
        super(MainWindow, self).__init__()
        self.gui = gui
        self.datastore = gui.ds
        self.user_proxy = gui.user_ds

        self.__menuBar = QtGui.QMenuBar(self)

        # File menu
        menuStructure = [
                ("File", [
                    ("Add Binary file...", self.doAddBinary, None),
                    ("Add Intel Hex file...", self.doAddIHEX, None),
                    ("Import properties...", self.doAddProps, None),
                    ("Save properties...", self.doSaveProps, None)
                    ]),
                ("Edit", [
                    ("Undo", self.doUndo, QtGui.QKeySequence.Undo),
                    ("Redo", self.doRedo, QtGui.QKeySequence.Redo)
                    ])
                ]

        for menuname, entries in menuStructure:
            m = QtGui.QMenu(menuname, self)
            for itemname, action, seq in entries:
                a = m.addAction(QtGui.QIcon(), itemname, None,
                        QtGui.QKeySequence(seq))
                a.triggered.connect(action)

            self.menuBar().addMenu(m)

        self.resize(1200, 600)
        self.setWindowTitle(filename)

        self.disassemblyWidget = DisassemblyWidget(self, gui, self.datastore,
                self.user_proxy)

        self.setCentralWidget(self.disassemblyWidget)
        self.subviews = SubViewManager(self)

    def doUndo(self):
        self.datastore.cmdlist.rewind(1)
        self.disassemblyWidget.update()

    def doRedo(self):
        pass

    def doAddBinary(self, addr):
        # FIXME: use command pattern
        filename, filter = QtGui.QFileDialog.getOpenFileName()
        if not filename:
            return

        bpw = AddBinaryPromptWindow()
        bpw.exec_()
        base_addr = int(bpw.baseEdit.text(), 0)
        start_offset = int(bpw.startEdit.text(), 0)
        length = int(bpw.lengthEdit.text(), 0)
        applogic.tools_loaders.addBinary(self.datastore,
            filename, base_addr, start_offset, length)

    def doAddIHEX(self, addr):
        # FIXME: use command pattern
        filename, filter = QtGui.QFileDialog.getOpenFileName()
        if filename:
            applogic.tools_loaders.addIHex(self.datastore, filename)

    # Loads a json-format set of properties
    # Useful for importing from other tools, or when the DB format
    # has been very much broken
    def doAddProps(self, ident):
        filename, filter = QtGui.QFileDialog.getOpenFileName()
        if not filename:
            return
        ostruct = json.load(open(filename))

        c = CompoundCommand()

        for k, v in ostruct.iteritems():
            ident = int(k, 0)
            for setting, val in v.iteritems():
                if setting == "label":
                    c.add(SymbolNameCommand(ident, val))
                elif setting == "comment":
                    c.add(CommentCommand(ident,
                        CommentPosition.POSITION_RIGHT, val))

        self.datastore.cmdlist.push(c)

    def doSaveProps(self, addr):
        pass
