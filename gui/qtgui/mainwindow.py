from PyQt5 import QtCore, QtGui, QtWidgets

from subviewmgr import SubViewManager

# Force SubViews to be loaded
import subviews

from disassemblywidget import DisassemblyWidget

from datastore.dbtypes import CommentPosition

from applogic.cmd import CompoundCommand, SymbolNameCommand, CommentCommand
import applogic.tools_loaders

import json


class AddBinaryPromptWindow(QtWidgets.QDialog):
    def __init__(self):
        super(AddBinaryPromptWindow, self).__init__()

        # Todo - make validator that changes background red for bad values
        # and disables okButton

        # TODO: add cancel button

        # TODO: remove close and make act like a normal dialog
        okButton = QtWidgets.QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtWidgets.QDialogButtonBox.ActionRole)

        self.formLayout = QtWidgets.QFormLayout()
        self.baseEdit = QtWidgets.QLineEdit("0x0")
        self.startEdit = QtWidgets.QLineEdit("0x0")
        self.lengthEdit = QtWidgets.QLineEdit("-1")
        self.bitsEdit = QtWidgets.QLineEdit("8")

        self.formLayout.addRow("&Base Address:", self.baseEdit)
        self.formLayout.addRow("&Start Offset:", self.startEdit)
        self.formLayout.addRow("&Length:", self.lengthEdit)

        self.formLayout.addRow("&bits per unit:", self.bitsEdit)

        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, gui, filename):
        super(MainWindow, self).__init__()
        self.gui = gui
        self.datastore = gui.ds
        self.user_proxy = gui.user_ds

        self.__menuBar = QtWidgets.QMenuBar(self)

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
            m = QtWidgets.QMenu(menuname, self)
            for itemname, action, seq in entries:
                a = m.addAction(QtGui.QIcon(), itemname)
                if seq:
                    a.shortcut = QtGui.QKeySequence(seq)
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

    def doAddBinary(self):
        # FIXME: use command pattern
        filename, filter = QtWidgets.QFileDialog.getOpenFileName()
        if not filename:
            return

        bpw = AddBinaryPromptWindow()
        bpw.exec_()
        base_addr = int(bpw.baseEdit.text(), 0)
        start_offset = int(bpw.startEdit.text(), 0)
        length = int(bpw.lengthEdit.text(), 0)
        bits = int(bpw.bitsEdit.text(), 0)

        applogic.tools_loaders.addBinary(self.datastore,
            filename, base_addr, start_offset, length, bits)

    def doAddIHEX(self):
        # FIXME: use command pattern
        filename, filter = QtWidgets.QFileDialog.getOpenFileName()
        if filename:
            applogic.tools_loaders.addIHex(self.datastore, filename)

    # Loads a json-format set of properties
    # Useful for importing from other tools, or when the DB format
    # has been very much broken
    def doAddProps(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName()
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

    def doSaveProps(self):
        raise NotImplementedError("Save Props not implemented")
