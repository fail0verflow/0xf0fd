from PySide import QtGui, QtCore

from disassemblywidget import DisassemblyWidget
from symbolwidget import SymbolWidget

import applogic.tools_loaders


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

        self.__menuBar = QtGui.QMenuBar(self)

        # File menu
        self.fileMenu = QtGui.QMenu("File", self)
        self.addBinaryAction = self.fileMenu.addAction("Add Binary file...")
        self.addIHEXAction = self.fileMenu.addAction("Add Intel hex file...")

        self.addBinaryAction.triggered.connect(self.doAddBinary)
        self.addIHEXAction.triggered.connect(self.doAddIHEX)

        # Edit menu
        self.editMenu = QtGui.QMenu("Edit", self)
        self.undoAction = self.editMenu.addAction("Undo")
        self.redoAction = self.editMenu.addAction("Redo")

        self.undoAction.triggered.connect(self.doUndo)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        #self.setMenuBar(self.__menuBar)

        self.resize(800, 600)
        self.setWindowTitle(filename)

        self.disassemblyWidget = DisassemblyWidget(self, gui, self.datastore)
        symbolWidget = SymbolWidget(self, self.datastore)

        symbolWidget.widget.symbolSelected.connect(
            self.disassemblyWidget.gotoIdentSL)

        self.setCentralWidget(self.disassemblyWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, symbolWidget)

    def doUndo(self):
        self.datastore.cmdlist.rewind(1)
        self.disassemblyWidget.update()

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
