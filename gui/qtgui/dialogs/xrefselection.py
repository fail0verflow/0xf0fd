from PySide import QtCore
from PySide import QtGui
from applogic import util


class XrefSelectionWindow(QtGui.QDialog):
    def __init__(self, ds, xreflist):
        super(XrefSelectionWindow, self).__init__()

        self.__xrl = xreflist

        self.formLayout = QtGui.QVBoxLayout()

        self.okButton = QtGui.QPushButton("OK")
        self.okButton.setDefault(True)
        self.okButton.clicked.connect(self.accept)

        self.xrsw = QtGui.QListWidget()

        # Add formatted xrefs to xref window
        for i in xreflist:
            QtGui.QListWidgetItem(
                    util.formatIdent(ds, i.ident_from), self.xrsw)

        self.xrsw.setCurrentRow(0)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(self.okButton, QtGui.QDialogButtonBox.ActionRole)

        self.formLayout.addWidget(self.xrsw)
        self.formLayout.addWidget(buttonBox)

        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

    # Get address to goto; valid on successful completion
    def getSelectedAddr(self):
        citem = self.xrsw.currentRow()

        if citem == None:
            return None

        return self.__xrl[citem].ident_from
