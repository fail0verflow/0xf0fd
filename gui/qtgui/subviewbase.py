from PySide import QtGui, QtCore


class SubViewBase(QtGui.QDockWidget):
    closed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(SubViewBase, self).__init__(*args, **kwargs)

    def closeEvent(self, event):
        event.accept()
        self.closed.emit()
