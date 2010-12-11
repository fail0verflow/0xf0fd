from PySide import QtCore, QtGui
from idis.datastore import DataStore
from arch.shared_opcode_types import *
from command_handler import *

"""
class LineCounterMapper(object):
    def __init__(self, ds):
        self.ds = ds
        self.rebuild()
        
    def getLineCount(self):
        return self.row_count
    
    def getLine(self, line):
        return self.row_map[line]
        
    def rebuild(self):
        self.row_map = {}
        self.row_count = 0
        for i in self.ds.segments:
            addr = i.base_addr
            while addr < i.base_addr + i.length:
                dtype = self.ds[addr]
                self.row_map[self.row_count] = addr
                addr += dtype.length
                self.row_count += 1
        

class DisassemblyModel(QtCore.QAbstractItemModel):
    def __init__(self, ds):
        super(DisassemblyModel, self).__init__()
        self.ds = ds
        self.cm = LineCounterMapper(ds)
        
    def columnCount(self, parent):
        return 2
        
    def rowCount(self, parent):
        return self.cm.getLineCount()
        
    def index(self, row, col, parent):
        return self.createIndex(row, col)
        
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            line_addr = self.cm.getLine(index.row())
            if index.column() == 0:
                return "%04x" % line_addr
            elif index.column() == 1:
                try:
            
                    return "%s" % ds[line_addr].disasm
                except KeyError:
                    return None
        return None
    
    def parent(self, index):
        return QtCore.QModelIndex()
""" 


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

STYLE_HEXADDR = 0x80001
STYLE_COMMENT = 0x80002
STYLE_OPCODE = 0x80003
STYLE_ARROW = 0x80004

class DisassemblyGraphicsView(QtGui.QWidget):
    def __init__(self, ds, mapper):
        QtGui.QWidget.__init__(self)

        
        self.arrowEnd = 75
        self.addrX = 80
        self.labelX = 140
        self.disasmX = 180
        self.firstOpcodeX = 230
        self.commentX = 360
        
        self.lineSpacing = 14
        
        self.ds = ds
        self.resize(800, 600)

        self.memaddr_top = 0
        self.memaddr_selected = 0
        
        self.font = QtGui.QFont("courier")
        self.font_bold = QtGui.QFont("courier", weight=75)

        self.line_addr_map = {}
    
        self.addr_line_map = {}
    def getClickAddr(self, y):
        lineIndex = y / self.lineSpacing
        return self.line_addr_map[lineIndex]
        
        
    def getTopAddr(self):
        return self.memaddr_top
        
    def setTopAddr(self, addr):
        self.memaddr_top = addr
        self.update()
        
    def getSelAddr(self):
        return self.memaddr_selected
        
    def setSelAddr(self, memaddr_selected):
        self.memaddr_selected = memaddr_selected
        self.update()
    
    # Apply styling to text to be drawn; depending on text type
    def applyStyle(self, p, styleType):
        symbolic_col = QtGui.QColor(0,200,0)
        fg_col = QtGui.QColor(0,0,0)

        comment_col = QtGui.QColor(127,127,127)
        opcode_col = QtGui.QColor(0,0,127)
        
        pen = p.pen()
        pen.setWidth(1)
        p.setPen(pen)

        if styleType == TYPE_SYMBOLIC:
            p.setBrush(symbolic_col)
            p.setPen(symbolic_col)
            p.setFont(self.font_bold)
        elif styleType == STYLE_COMMENT:
            p.setBrush(comment_col)
            p.setPen(comment_col)
            p.setFont(self.font)
        elif styleType == STYLE_OPCODE:
            p.setBrush(opcode_col)
            p.setPen(opcode_col)
            p.setFont(self.font)
        elif styleType == STYLE_ARROW:
            p.setBrush(fg_col)
            p.setPen(fg_col)
            pen = p.pen()
            pen.setWidth(2)
            p.setPen(pen)
            p.setFont(self.font)
        else:
            p.setBrush(fg_col)
            p.setPen(fg_col)
            p.setFont(self.font)
            
    
    def drawArrow(self, p, col, startLine, endLine):
        asp = startLine * self.lineSpacing + self.lineSpacing/2
        aep = endLine * self.lineSpacing + self.lineSpacing/2
        p.drawLine(col, asp, self.arrowEnd, asp)
        p.drawLine(col, asp, col, aep)
        p.drawLine(col, aep, self.arrowEnd, aep)
        p.drawLine(self.arrowEnd-3, aep-3, self.arrowEnd, aep)
        p.drawLine(self.arrowEnd-3, aep+3, self.arrowEnd, aep)

        
    def paintEvent(self, event):
        arrows = []
        
        self.line_addr_map = {}
        self.addr_line_map = {}
        
        # Calculate maximum number of lines on the screen
        nlines = self.geometry().height() / self.lineSpacing
        
        p = QtGui.QPainter()
        p.begin(self)
        p.setFont(self.font)
        
        try:
            # Erase the widget
            bg_brush = QtGui.QBrush(QtGui.QColor(255,255,255))
            p.fillRect(self.geometry(), bg_brush)
            
            # line marker background
            ln_brush1 = QtGui.QColor(250,250,255)
            
            # selected line background
            sel_line =  QtGui.QColor(200,200,255)

            line_memaddr = self.memaddr_top

            i = 0
            i_mod = 0
            while i < nlines:
                try:
                    line_data = self.ds[line_memaddr]
                except KeyError:
                    line_memaddr += 1
                    break
                    continue
                    
                # Calculate the top and text baseline of the line   
                linetop = self.lineSpacing * i
                def cBaseLine(ln):
                    return linetop + self.lineSpacing * ln + 12
                
                #
                # layout is:
                #   0001
                #   0001   label: 
                #   0001       opcode
                #   0002
                #
                #
                
                lines_needed = 1
                disasm_start = 0
                
                label = line_data.label
                if label:
                    lines_needed += 2
                    disasm_start += 2
                    label_start   = 1
                
                # draw the background of the line
                if line_memaddr == self.memaddr_selected:
                    p.fillRect(0,linetop,self.geometry().width(),self.lineSpacing*lines_needed, sel_line)
                elif (i_mod) % 2 == 0:
                    p.fillRect(0,linetop,self.geometry().width(),self.lineSpacing*lines_needed, ln_brush1)

                # draw the label [if any]
                if label:
                    self.applyStyle(p, TYPE_SYMBOLIC)
                    p.drawText(self.labelX, cBaseLine(label_start), "%s:" % label)


                opcode = line_data.disasm.opcode
                
                # Draw addresses
                self.applyStyle(p, STYLE_HEXADDR)
                for indiv_line in xrange(lines_needed):
                    self.line_addr_map[indiv_line + i] = line_memaddr
                    p.drawText(self.addrX, cBaseLine(indiv_line), "%04x:" % line_memaddr)
                
                
                self.applyStyle(p, STYLE_OPCODE)
                p.drawText(self.disasmX, cBaseLine(disasm_start), "%s" % opcode)
                
                
                self.addr_line_map[line_memaddr] = disasm_start + i
                
                try:
                    arrows += [ (line_data.addr, dest) 
                                for dest in line_data.cdict["decoding"]["dests"] 
                                if dest != line_data.addr + line_data.length]
                except KeyError:
                    pass
                    
                opcodeX = self.firstOpcodeX             
                for opcode_num in xrange(len(line_data.disasm.operands)):
                    operand = line_data.disasm.operands[opcode_num]
                    last_operand = opcode_num == len(line_data.disasm.operands) - 1
                    
                    text, opc_type = operand.render(self.ds)
                    
                    self.applyStyle(p, opc_type)
                    opcode_text = text
                    opcode_width = p.fontMetrics().width(opcode_text);
                    p.drawText(opcodeX, cBaseLine(disasm_start), opcode_text)
                    opcodeX += opcode_width
                    
                    
                    # Draw the ", " separator
                    self.applyStyle(p, None)
                    if not last_operand:
                        p.drawText(opcodeX, cBaseLine(disasm_start), ", ")
                        opcodeX += p.fontMetrics().width(", ");


                if line_data.comment:
                    self.applyStyle(p, STYLE_COMMENT)
                    p.drawText(self.commentX, cBaseLine(disasm_start), "; %s" % line_data.comment)
                    
                line_memaddr += line_data.length
                i += lines_needed
                i_mod += 1
            
            self.applyStyle(p, STYLE_ARROW)
            arrows = [ (src, dst)
                        for src, dst in arrows
                        if src in self.addr_line_map and dst in self.addr_line_map ]

            def arrowcompare(a, b):
                asrc, adst = a
                bsrc, bdst = b
                
                if asrc < bsrc and adst > bdst: return 1
                if asrc > bsrc and adst < bdst: return -1
                
                return 0
                
            arrows.sort(arrowcompare)
            arrows = arrows[::-1]
            
            pos = 67
            for src, dst in arrows:
                self.drawArrow(p, pos, self.addr_line_map[src], self.addr_line_map[dst])
                pos -= 12
        finally:
            p.end()
        
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

class MainWindow(QtGui.QWidget):
    def __init__(self, ds, filename):
        super(MainWindow, self).__init__()
        
        self.resize(800,600)
        self.setWindowTitle(filename)
        
        view = DisassemblyWidget(self, ds)
        
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(view)
        
        self.setLayout(mainLayout)
        
import sys
class QTGui(object):
    def __init__(self):
        pass
    def startup(self):
        pass

    def mainloop(self, filenames):
        if (len(filenames) < 1):
            print "usage: idis filename"
            sys.exit(-1)

        ds = DataStore(filenames[0])

        app = QtGui.QApplication(sys.argv)

        mainWin = MainWindow(ds, filenames[0])
        mainWin.show()

        app.exec_()


    def shutdown(self):
        pass


