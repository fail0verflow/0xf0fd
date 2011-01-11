from PySide import QtCore, QtGui
from arch.shared_opcode_types import *
from idis.dbtypes import CommentPosition
from textview import FDTextArea, FDTextAttribs
from arrow_view import FDArrowView

STYLE_HEXADDR = 0x80001
STYLE_COMMENT = 0x80002
STYLE_OPCODE = 0x80003
STYLE_DIVIDER = 0x80008

TA = FDTextAttribs

class DisassemblyGraphicsView(QtGui.QWidget):
    def __init__(self, ds, mapper):
        QtGui.QWidget.__init__(self)

        
        self.addrX = 0
        self.labelX = 12
        self.disasmX = 14
        self.firstOpcodeX = 25
        self.commentX = 50
       
        self.sel_color = QtGui.QColor(190, 190, 255)
        
        self.ds = ds
        self.resize(800, 600)

        self.memaddr_top = 0
        self.memaddr_selected = 0
        
        # Used for calculating clicks
        self.line_addr_map = {}

        # Used for drawing arrows
        self.addr_line_map = {}

        self.arrowWidth = 80

        self.atv = FDTextArea(self.arrowWidth, 0, self.width() - self.arrowWidth, self.height())
        self.arv = FDArrowView(0, 0, self.arrowWidth, self.height(), self.atv.c_height)

        self.setSizes()

    def setSizes(self):
        self.atv.resize(self.width() - self.arrowWidth, self.height())
        self.arv.resize(self.arrowWidth, self.height())

    def getClickAddr(self, x, y):
        lineIndex, char, tag = self.atv.mapCoords(x, y)
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
   
    def resizeEvent(self, event):
        super(DisassemblyGraphicsView, self).resizeEvent(event)
        self.setSizes()

    # Apply styling to text to be drawn; depending on object type
    # FIXME: This should pull styling info from the config
    def getStyle(self, styleType, selected=False):
        symbolic_col        = QtGui.QColor(  0, 200,   0)
        fg_col              = QtGui.QColor(  0,   0,   0)
        comment_col         = QtGui.QColor(127, 127, 127)
        opcode_col          = QtGui.QColor(  0,   0, 127)        
        divider_col         = QtGui.QColor(180, 180, 180)

        if styleType == TYPE_SYMBOLIC:
            return TA(color=symbolic_col, isBold=True)

        elif styleType == STYLE_COMMENT:
            return TA(color=comment_col)

        elif styleType == STYLE_OPCODE:
            return TA(color=opcode_col)

        elif styleType == STYLE_DIVIDER:
            return TA(color=divider_col)

        else:
            return TA(color=fg_col) 

    def calculateLineParameters(self, data):
        lines_needed = 1
        disasm_start = 0
        label_start = 0
        divider_start = None

        if data.label:
            lines_needed += 2
            disasm_start += 2
            label_start = 1

        try:
            if data.addr + data.length not in data.disasm.dests():
                lines_needed += 2
                divider_start = disasm_start+1

        except AttributeError:
            pass

        return lines_needed, disasm_start, label_start, divider_start

    def calculateAddressLinecount(self, data):
        return calculateLineParameters(data)[0]

    def drawWidget(self, p):
        self.atv.clear()
        self.arv.clear()

        self.line_addr_map = {}
        self.addr_line_map = {}
        
        # Calculate maximum number of lines on the screen
        nlines = self.atv.nlines
        
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
                
            #
            # layout is:
            #   0001
            #   0001   label: 
            #   0001       opcode
            #   0002
            #
            #
            
            lines_needed, disasm_start, label_start, divider_start = self.calculateLineParameters(line_data)
            label = line_data.label            

            # draw the label [if any]
            if label:
                self.atv.addText(i+label_start, self.labelX, "%s:" % label, self.getStyle(TYPE_SYMBOLIC))


            opcode = line_data.disasm.mnemonic
            
            # Draw addresses
            for indiv_line in xrange(lines_needed):
                self.line_addr_map[indiv_line + i] = line_memaddr
                self.atv.addText(indiv_line + i, self.addrX, "%08x:" % line_memaddr, self.getStyle(STYLE_HEXADDR))
            
           
            # Draw opcode
            self.atv.addText(i+disasm_start, self.disasmX, "%s" % opcode, self.getStyle(STYLE_OPCODE))
            
            
            self.addr_line_map[line_memaddr] = disasm_start + i
           
            # Add addr to disasm
            try:
                for arrow in [ (line_data.addr, dest) 
                            for dest in line_data.disasm.dests()
                            if dest != line_data.addr + line_data.length]:
                    self.arv.addArrow(arrow[0], arrow[1])

            except AttributeError:
                pass
            
            # Draw destination
            opcodeX = self.firstOpcodeX             
            for opcode_num in xrange(len(line_data.disasm.operands)):
                operand = line_data.disasm.operands[opcode_num]
                last_operand = opcode_num == len(line_data.disasm.operands) - 1
                
                text, opc_type = operand.render(self.ds)
                
                opcode_text = text
                self.atv.addText(i+disasm_start, opcodeX, opcode_text, self.getStyle(opc_type), opcode_text)
                opcodeX += len(opcode_text)
                
                
                # Draw the ", " separator
                if not last_operand:
                    separator = ", "
                    self.atv.addText(i+disasm_start, opcodeX, separator, None)
                    opcodeX += len(separator)

            # Draw comment
            comment = self.ds.comments.getCommentText(line_memaddr, CommentPosition.POSITION_RIGHT) 
            if comment:
                self.atv.addText(i+disasm_start, self.commentX, "; %s" % comment, self.getStyle(STYLE_COMMENT))
            
            # Draw divider
            if divider_start != None:
                self.atv.addText(i+divider_start, self.disasmX, "-" * 60, self.getStyle(STYLE_DIVIDER))

            line_memaddr += line_data.length
            i += lines_needed
            i_mod += 1

        try:
            self.atv.setRowHighlight(self.addr_line_map[self.memaddr_selected], self.sel_color)
        except KeyError:
            pass

        self.atv.drawArea(p)
        self.arv.render(p,self.addr_line_map)



    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        # Wrap the actual paint code to prevent QT crashes
        # if we throw an exception
        try:
            self.drawWidget(p)
        finally:
            p.end()

