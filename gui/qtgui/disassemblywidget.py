from disassemblyview import DisassemblyGraphicsView
from PySide import QtCore, QtGui
from command_handler import *


class SegmentLineMapper(object):
    def __init__(self, ds):
        self.ds = ds

    def getLineCount(self):
        return sum([i.size for i in self.ds.segments])

    def mapIdentToLine(self, ident):
        line = 0
        for i in self.ds.segments:
            try:
                int_addr = i.mapIn(ident)
            except:
                line += i.size
                continue

            return line + int_addr - i.start_addr

    def mapLineToIdent(self, line):
        for i in self.ds.segments:
            if line < i.size:
                return i.mapOut(line + i.start_addr)

            line -= i.size
        raise ValueError("Address could not be mapped")


class DisassemblyWidget(QtGui.QAbstractScrollArea):
    def __init__(self, parent, gui, ds):
        super(DisassemblyWidget, self).__init__(parent)
        self.window_up = parent

        self.sm = SegmentLineMapper(ds)
        self.ds = ds
        self.view = DisassemblyGraphicsView(self.ds, self.sm)

        self.setViewport(self.view)
        self.ch = CommandHandler(gui, self.ds, self)

        # Setup scrollbars
        self.reconfigureScrollBars()
        self.ds.layoutChanged.connect(self.reconfigureScrollBars)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Connect scrolling to update the view
        QtCore.QObject.connect(self.vscroll,
            QtCore.SIGNAL('valueChanged(int)'), self.scrollEvent)

    def reconfigureScrollBars(self):
        self.vscroll = self.verticalScrollBar()
        self.vscroll.setMinimum(0)
        self.vscroll.setMaximum(self.sm.getLineCount() - 1)

    def keyPressEvent(self, evt):
        reserved_keys = []

        if evt.k in reserved_keys:
            super(DisassemblyWidget, self).keyPressEvent(evt)
        else:
            if evt.k == QtCore.Qt.Key_Down:
                selected_addr = self.view.getSelAddr()
                next_addr = selected_addr + self.ds[selected_addr].length
                self.view.setSelAddr(next_addr)

            elif evt.k == QtCore.Qt.Key_Up:
                selected_addr = self.view.getSelAddr()
                next_addr = self.ds.findStartForAddress(selected_addr - 1)

                if next_addr == None:
                    return

                if next_addr < self.view.getTopAddr():
                    self.view.setTopAddr(next_addr)

                self.view.setSelAddr(next_addr)

            else:
                self.ch.handleCommand(self.view.getSelAddr(), evt.k)
                self.view.update()
                self.ds.flush()

    def update(self):
        self.view.update()

    # Hack to work around Pyside forcing longs->ints
    @QtCore.Slot(tuple)
    def gotoIdentSL(self, tup):
        self.gotoIdent(tup[0])

    def gotoIdent(self, val, top=None):
        if top == None:
            top = val

        self.view.setTopAddr(top)
        self.view.setSelAddr(val)
        self.vscroll.setValue(self.sm.mapIdentToLine(top))

    def mousePressEvent(self, evt):
        self.view.setSelAddr(self.view.getClickAddr(evt.x(), evt.y()))

    def scrollEvent(self, value):
        mapped_addr = self.sm.mapLineToIdent(value)
        seek_addr = self.ds.findStartForAddress(mapped_addr)

        assert seek_addr != None
        self.view.setTopAddr(seek_addr)

    def paintEvent(self, event):
        self.view.paintEvent(event)

    def resizeEvent(self, event):
        super(DisassemblyWidget, self).resizeEvent(event)
        self.view.resizeEvent(None)
