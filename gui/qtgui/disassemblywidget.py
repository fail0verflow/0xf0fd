from disassemblyview import DisassemblyGraphicsView
from PyQt5 import QtCore, QtGui, QtWidgets
from command_handler import *
from datastore import InfoStore


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


class DisassemblyWidget(QtWidgets.QAbstractScrollArea):
    def __init__(self, parent, gui, ds, user_proxy):
        super(DisassemblyWidget, self).__init__(parent)
        self.window_up = parent

        self.memstack = []

        self.sm = SegmentLineMapper(user_proxy)
        self.user_proxy = user_proxy
        self.ds = ds
        self.view = DisassemblyGraphicsView(user_proxy, self.sm)

        self.setViewport(self.view)
        self.ch = CommandHandler(gui, self.ds, self)

        # Setup scrollbars
        self.reconfigureScrollBars()
        self.ds.layoutChanged.connect(self.reconfigureScrollBars)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Connect scrolling to update the view
        self.vscroll.valueChanged[int].connect(self.scrollEvent)

    def reconfigureScrollBars(self):
        self.vscroll = self.verticalScrollBar()
        self.vscroll.setMinimum(0)
        self.vscroll.setMaximum(self.sm.getLineCount() - 1)

    def keyPressEvent(self, evt):
        reserved_keys = []
        try:
            key = evt.k
        except AttributeError:
            key = evt.key()

        if key in reserved_keys:
            super(DisassemblyWidget, self).keyPressEvent(evt)
        else:
            if key == QtCore.Qt.Key_Down:
                selected_addr = self.view.getSelAddr()
                rc, obj = self.user_proxy.infostore.lookup(selected_addr)
                if rc != InfoStore.LKUP_OK:
                    return

                next_addr = selected_addr + obj.length

                self.view.setSelAddr(next_addr)

                ad = self.view.getTopAddr()
                if next_addr > self.view.lastDrawnAddr:
                    while next_addr > self.view. \
                            calculateLastFullyDrawnAddr(ad):

                        to_rc, top_obj = self.user_proxy. \
                            infostore.lookup(ad)

                        if to_rc != InfoStore.LKUP_OK:
                            return

                        ad += top_obj.length

                    self.view.setTopAddr(ad)

            elif key == QtCore.Qt.Key_Up:
                selected_addr = self.view.getSelAddr()

                next_addr = self.user_proxy.infostore.findStartForAddress(
                    selected_addr - 1)

                if next_addr == None:
                    return

                # rewind view to prev line if selected line is outside of shown
                # area
                if next_addr < self.view.getTopAddr():
                    self.view.setTopAddr(next_addr)

                self.view.setSelAddr(next_addr)

            else:
                self.ch.handleCommand(self.view.getSelAddr(), key)
                self.view.update()
                self.ds.flush()

    def update(self):
        self.view.update()

    # With silly tuple hack to work around PySide bugs
    @QtCore.pyqtSlot(tuple)
    def navigateToIdentSL(self, val):
        self.navigateToIdent(val[0])

    # 'Nice' navigation; attempt to select ident if it's already onscreen
    # or jump to the ident if it's offscreen
    # Also, track memory stack movements
    def navigateToIdent(self, val, supress_memstack=False):
        if not supress_memstack:
            self.memstack.append(
                (self.view.getTopAddr(), self.view.getSelAddr()))

        if val <= self.view.lastDrawnAddr and val >= self.view.getTopAddr():
            self.view.setSelAddr(val)
        else:
            self.setTopSelectedIdent(val)

    # Hack to work around Pyside forcing longs->ints
    @QtCore.pyqtSlot(tuple)
    def setTopSelectedIdentSL(self, tup):
        self.setTopSelectedIdent(tup[0])

    def setTopSelectedIdent(self, val, top=None):
        if top == None:
            top = val

        self.view.setTopAddr(top)
        self.view.setSelAddr(val)
        self.vscroll.setValue(self.sm.mapIdentToLine(top))

    def mousePressEvent(self, evt):
        self.view.setSelAddr(self.view.getClickAddr(evt.x(), evt.y()))

    def scrollEvent(self, value):
        try:
            mapped_addr = self.sm.mapLineToIdent(value)
        except ValueError:
            return

        # Use user_proxy here since the user_proxy will generate lines
        # where none are otherwise
        seek_addr = self.user_proxy.infostore.findStartForAddress(mapped_addr)

        assert seek_addr != None
        self.view.setTopAddr(seek_addr)

    def paintEvent(self, event):
        self.view.paintEvent(event)

    def resizeEvent(self, event):
        super(DisassemblyWidget, self).resizeEvent(event)
        self.view.resizeEvent(None)
