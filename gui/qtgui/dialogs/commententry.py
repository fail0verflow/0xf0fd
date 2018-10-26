from PyQt5 import QtCore, QtGui, QtWidgets
from datastore import CommentPosition


class CommentEntryTextField(QtWidgets.QTextEdit):

    # Signal that indicates magic-exit keystroke was entered
    # to terminate dialog
    magicExitPressed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        QtWidgets.QTextEdit.__init__(self, *args, **kwargs)

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


class AddCommentWindow(QtWidgets.QDialog):
    def __init__(self, position, oldcomment):
        super(AddCommentWindow, self).__init__()

        positionText = {
            CommentPosition.POSITION_BEFORE: "Pre-line comment",
            CommentPosition.POSITION_RIGHT:  "Line comment",
            CommentPosition.POSITION_BOTTOM: "Post-line comment"
            }[position]

        okButton = QtWidgets.QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtWidgets.QDialogButtonBox.ActionRole)

        self.formLayout = QtWidgets.QFormLayout()
        self.positionLabel = QtWidgets.QLabel(positionText)
        self.edit = CommentEntryTextField(oldcomment)

        self.edit.magicExitPressed.connect(self.accept)

        self.formLayout.addRow("&Position:", self.positionLabel)
        self.formLayout.addRow("&Comment text:", self.edit)

        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
