from PySide import QtCore, QtGui
from subviewbase import SubViewBase

import StringIO
import code
import sys
import traceback


class output_to_console(object):
    def __init__(self, output_callback):
        self.ocb = output_callback

        self.stdout_sio = StringIO.StringIO()
        self.stderr_sio = StringIO.StringIO()

    def __enter__(self):
        self.stdout_save = sys.stdout
        self.stderr_save = sys.stderr
        self.stdin_save = sys.stdin

        sys.stdin = None
        sys.stdout = self.stdout_sio
        sys.stderr = self.stderr_sio

    def __exit__(self, excType, excValue, excTB):

        sys.stdout = self.stdout_save
        sys.stderr = self.stderr_save
        sys.stdin = self.stdin_save

        self.ocb(1, self.stdout_sio.getvalue())
        self.ocb(2, self.stderr_sio.getvalue())

        if excType:
            exc = "".join(traceback.format_exception(excType, excValue, excTB))
            self.ocb(2, exc)


class ConsoleWidget(QtGui.QWidget):

    def __init__(self, parent_win, ds):
        super(ConsoleWidget, self).__init__()
        self.main_win = parent_win
        self.ds = ds

        self.layout = QtGui.QVBoxLayout()

        self.cons = code.InteractiveConsole(
                {
                    'main_win': self.main_win,
                    'datastore': self.ds,
                    'ds': self.ds
                })

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFontPointSize(10)

        self.entry = QtGui.QLineEdit()
        self.entry.returnPressed.connect(self.returnPressed)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.entry)

        self.setLayout(self.layout)

    def sizeHint(self):
        return QtCore.QSize(0, 100)

    def textOutput(self, fd, v):
        if (v):
            self.output.append(v.strip())

    def returnPressed(self):
        t = self.entry.text().strip()

        self.output.append(">>> %s" % t)
        with output_to_console(self.textOutput):
            self.cons.push(t)

        self.entry.clear()


class ConsoleSubView(SubViewBase):
    def __init__(self, parent_win, ds):
        super(ConsoleSubView, self).__init__("Console", parent_win)

        self.widget = ConsoleWidget(self, ds)
        self.setWidget(self.widget)
