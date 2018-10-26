from PyQt5 import QtCore, QtGui, QtWidgets


class SubViewBase(QtWidgets.QDockWidget):
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(SubViewBase, self).__init__(*args, **kwargs)

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()
