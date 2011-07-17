from PySide import QtCore
from PySide import QtGui

from applogic import util

from datastore import CommentPosition


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


class CommentEntryTextField(QtGui.QTextEdit):

    # Signal that indicates magic-exit keystroke was entered
    # to terminate dialog
    magicExitPressed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        QtGui.QTextEdit.__init__(self, *args, **kwargs)

    def keyPressEvent(self, evt):

        # Check for control-enter or command-enter
        if evt.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return) and \
            evt.modifiers() & (QtCore.Qt.ControlModifier |
                    QtCore.Qt.MetaModifier):

            # If control or command enter, emit our "magic exit" event to
            # terminate the dialog
            self.magicExitPressed.emit()
            return

        super(CommentEntryTextField, self).keyPressEvent(evt)


class AddCommentWindow(QtGui.QDialog):
    def __init__(self, position, oldcomment):
        super(AddCommentWindow, self).__init__()

        positionText = {
            CommentPosition.POSITION_BEFORE: "Pre-line comment",
            CommentPosition.POSITION_RIGHT:  "Line comment",
            CommentPosition.POSITION_BOTTOM: "Post-line comment"
            }[position]

        okButton = QtGui.QPushButton("OK")
        okButton.setDefault(True)
        QtCore.QObject.connect(okButton,
            QtCore.SIGNAL('clicked()'), self.accept)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtGui.QDialogButtonBox.ActionRole)

        self.formLayout = QtGui.QFormLayout()
        self.positionLabel = QtGui.QLabel(positionText)
        self.edit = CommentEntryTextField(oldcomment)

        QtCore.QObject.connect(self.edit,
            QtCore.SIGNAL('magicExitPressed()'), self.accept)

        self.formLayout.addRow("&Position:", self.positionLabel)
        self.formLayout.addRow("&Comment text:", self.edit)

        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
