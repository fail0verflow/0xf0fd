from PySide import QtCore, QtGui
from subviewbase import SubViewBase

import StringIO
import code
import sys
import traceback
import re


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


class MyLineEdit(QtGui.QLineEdit):
    keyUpEvent = QtCore.Signal()
    keyDownEvent = QtCore.Signal()
    keyTabEvent = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(MyLineEdit, self).__init__()

    def keyUp(self):
        self.keyUpEvent.emit()

    def keyDown(self):
        self.keyDownEvent.emit()

    def keyTab(self):
        self.keyTabEvent.emit()

    def event(self, evt):
        if evt.type() in \
                (QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease) and \
                evt.key() == QtCore.Qt.Key_Tab:
                    if evt.type() == QtCore.QEvent.KeyPress:
                        self.keyPressEvent(evt)
                    evt.accept()  # Do we need this?
                    return True
        else:
            return super(MyLineEdit, self).event(evt)

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Up:
            self.keyUp()
        elif evt.key() == QtCore.Qt.Key_Down:
            self.keyDown()
        elif evt.key() == QtCore.Qt.Key_Tab:
            self.keyTab()
        else:
            super(MyLineEdit, self).keyPressEvent(evt)


class ConsoleWidget(QtGui.QWidget):
    actionOccurred = QtCore.Signal()

    def __init__(self, parent_win, ds):
        super(ConsoleWidget, self).__init__()
        self.main_win = parent_win
        self.ds = ds

        self.history = []

        self.layout = QtGui.QVBoxLayout()

        self.ctx = {
                    'main_win': self.main_win,
                    'datastore': self.ds,
                    'ds': self.ds
                }

        self.cons = code.InteractiveConsole(self.ctx)

        self.output = QtGui.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFontPointSize(10)

        self.entry = MyLineEdit()
        self.entry.returnPressed.connect(self.returnPressed)
        self.entry.keyUpEvent.connect(self.keyUpPressed)
        self.entry.keyDownEvent.connect(self.keyDownPressed)
        self.entry.keyTabEvent.connect(self.doAutoComplete)

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.entry)

        self.setLayout(self.layout)

        self.hist_index = -1
        self.last_press = None

    def sizeHint(self):
        return QtCore.QSize(0, 100)

    def textOutput(self, fd, v):
        if (v):
            self.output.append(v.strip())

    def returnPressed(self):
        self.hist_index = -1
        t = self.entry.text().strip()
        self.history.append(t)

        self.output.append(">>> %s" % t)
        with output_to_console(self.textOutput):
            self.cons.push(t)

        self.entry.clear()

        self.actionOccurred.emit()

    def keyUpPressed(self):
        self.hist_index = min(self.hist_index + 1, len(self.history) - 1)

        if self.history:
            self.entry.setText(self.history[
                len(self.history) - self.hist_index - 1])

    def keyDownPressed(self):
        self.hist_index = max(self.hist_index - 1, -1)

        if self.hist_index >= 0 and self.history:
            self.entry.setText(self.history[
                len(self.history) - self.hist_index - 1])
        elif self.hist_index == -1:
            self.entry.setText('')

    def doAutoComplete(self):
        ln = self.entry.text()

        # See if this is the second press on the same text
        second_press = ln == self.last_press
        self.last_press = ln

        ac_list, rm_prefix, add_prefix = \
                self.getAutoCompleteResults(ln[:self.entry.cursorPosition()])

        # Filter private / semiprivate members on first press
        if not second_press:
            ac_list = [i for i in ac_list if not i.startswith('_')]

        # Either show list or do autocompletion
        if len(ac_list) > 1:
            self.output.append(", ".join(['%s' % i for i in ac_list]))
        elif len(ac_list) == 1:
            assert ac_list[0].startswith(rm_prefix)
            ent = add_prefix + ac_list[0][len(rm_prefix):]
            self.entry.insert(ent)

    def getAutoCompleteResults(self, cmdlineToPos):

        actopos = cmdlineToPos.strip()

        if actopos:
            # Try to extract the variable we're operating on
            actopos = re.match(r'^(.*[^.\w])?([.\w]+)$', actopos)

            actopos = actopos.group(2)

        # If we have a trailing period, strip it and then print a dir of the
        # object pointed to
        if actopos.endswith('.'):
            actopos = actopos[:-1]

            try:
                e = eval(actopos, self.ctx)
                return dir(e), '', ''
            except Exception:
                pass

        else:
            # If no trailing period, first try evaluating the object, like it
            # had a trailing period
            try:
                e = eval(actopos, self.ctx)
                return dir(e), '', '.'

            except Exception:
                pass

            # we're trying to complete a partial name?
            p_lastperiod = actopos.rfind('.')

            # If there is no trailing last period, try and complete
            # in global scope and match full name
            if p_lastperiod == -1:
                per = ''
                gr = self.ctx.keys()
                trail = actopos
            else:
                per = ''
                st = actopos[:p_lastperiod]
                trail = actopos[p_lastperiod + 1:]

                try:
                    e = eval(st, self.ctx)
                    gr = dir(e)
                except Exception:
                    pass

            if gr:
                return [i for i in gr if i.startswith(trail)], trail, per


class ConsoleSubView(SubViewBase):
    def __init__(self, parent_win, ds):
        super(ConsoleSubView, self).__init__("Console", parent_win)

        self.widget = ConsoleWidget(self, ds)
        self.setWidget(self.widget)
