from disassemblyview import DisassemblyGraphicsView
from PySide import QtCore, QtGui
from command_handler import *



class SegmentLineMapper(object):
    def __init__(self, ds):
        self.ds = ds
        
    def getLineCount(self):
        return sum([i.length for i in self.ds.segments])
        
    def map(self, addr):
        line = 0
        
        for i in self.ds.segments:
            if addr >= i.base_addr and addr < (i.base_addr + i.length):
                return line + addr - i.base_addr
            line += i.length
            
        raise ValueError, "Address could not be mapped"
        

class DisassemblyWidget(QtGui.QAbstractScrollArea):
    def __init__(self, parent, ds):
        super(DisassemblyWidget, self).__init__(parent)
        self.window_up = parent

        self.sm = SegmentLineMapper(ds)
        self.ds = ds
        self.view = DisassemblyGraphicsView(self.ds, self.sm)

        self.setViewport(self.view)
        self.ch = CommandHandler(self.ds, self.view)
        
        vscroll = self.verticalScrollBar()
        vscroll.setMinimum(0)
        vscroll.setMaximum(self.sm.getLineCount())
        QtCore.QObject.connect(vscroll, QtCore.SIGNAL('valueChanged(int)'), self.scrollEvent)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def keyPressEvent(self, evt):
        reserved_keys = []
            
        if evt.k in reserved_keys:
            super(DisassemblyWidget, self).keyPressEvent(evt)
        else:
            if evt.k == QtCore.Qt.Key_Down:
                selected_addr = self.view.getSelAddr()
                next_addr = selected_addr + ds[selected_addr].length
                self.view.setSelAddr(next_addr)
            
            elif evt.k == QtCore.Qt.Key_Up:
                # Hack
                selected_addr = self.view.getSelAddr()
                next_addr = selected_addr - 1
                
                while 1:
                    if next_addr < 0:
                        next_addr = 0
                        break
                    try:
                        ds[next_addr]
                        break
                    except KeyError:
                        next_addr -= 1
                        
                self.view.setSelAddr(next_addr)
            else:
                self.ch.handleCommand(self.view.getSelAddr(), evt.k)
                self.view.update()
                self.ds.flush()
                
    def mousePressEvent(self, evt):
        self.view.setSelAddr(self.view.getClickAddr(evt.y()))
        
    def scrollEvent(self, value):
        self.view.setTopAddr(value)
        
    def paintEvent(self, event):
        self.view.paintEvent(event)



