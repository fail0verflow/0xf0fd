from PySide import QtCore, QtGui
from arch.shared_opcode_types import *


STYLE_HEXADDR = 0x80001
STYLE_COMMENT = 0x80002
STYLE_OPCODE = 0x80003
STYLE_ARROW_FWD = 0x80004
STYLE_ARROW_BACK = 0x80005
STYLE_ARROW_SEL_FWD = 0x80006
STYLE_ARROW_SEL_BACK = 0x80007

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

        # Used for calculating clicks
        self.line_addr_map = {}

        # Used for drawing arrows
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
    
    # Apply styling to text to be drawn; depending on object type
    # FIXME: This should pull styling info from the config
    def applyStyle(self, p, styleType):
        symbolic_col        = QtGui.QColor(  0, 200,   0)
        fg_col              = QtGui.QColor(  0,   0,   0)
        comment_col         = QtGui.QColor(127, 127, 127)
        opcode_col          = QtGui.QColor(  0,   0, 127)
        fwd_arrow_col       = QtGui.QColor(  0, 100,   0)
        back_arrow_col      = QtGui.QColor(100,   0,   0)
        fwd_sel_arrow_col   = QtGui.QColor(  0, 200,   0)
        back_sel_arrow_col  = QtGui.QColor(200,   0,   0)
        
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
        elif styleType in [STYLE_ARROW_FWD, STYLE_ARROW_SEL_FWD, STYLE_ARROW_BACK, STYLE_ARROW_SEL_BACK]:
            colour = {
                        STYLE_ARROW_FWD: fwd_arrow_col,
                        STYLE_ARROW_BACK: back_arrow_col,
                        STYLE_ARROW_SEL_FWD: fwd_sel_arrow_col,
                        STYLE_ARROW_SEL_BACK: back_sel_arrow_col
                     }[styleType]

            p.setBrush(colour)
            p.setPen(colour)
            pen = p.pen()
            pen.setWidth(2)
            p.setPen(pen)
        
        else:
            p.setBrush(fg_col)
            p.setPen(fg_col)
            p.setFont(self.font)
            
    
    def drawArrow(self, p, col, startLine, endLine, selected_line):
        # Style the arrow based on direction, and whether a source or destination
        # are selected
        selected = selected_line == startLine or selected_line == endLine
        forward = endLine > startLine
        style = { (False, False): STYLE_ARROW_BACK,
                  (False, True):  STYLE_ARROW_SEL_BACK,
                  (True,  False): STYLE_ARROW_FWD,
                  (True,  True):  STYLE_ARROW_SEL_FWD }[forward, selected]
        self.applyStyle(p, style)

        # Draw the lines of the arrow
        asp = startLine * self.lineSpacing + self.lineSpacing/2
        aep = endLine * self.lineSpacing + self.lineSpacing/2
        p.drawLine(col, asp, self.arrowEnd, asp)
        p.drawLine(col, asp, col, aep)
        p.drawLine(col, aep, self.arrowEnd, aep)

        # Draw the arrowhead
        p.drawLine(self.arrowEnd-3, aep-3, self.arrowEnd, aep)
        p.drawLine(self.arrowEnd-3, aep+3, self.arrowEnd, aep)

    def drawArrows(self, p, arrows):

        class Arrow(object):
            def __init__(self, src, dst):
                self.src = src
                self.dst = dst
                self.higher_arrows = []
                self.min_x = 1234
                self.dependents = 0
                self.drawn = False
                self.begin = min(src, dst)
                self.end = max(src, dst)
            def __str__(self):
                return "%04x -> %04x, [%d]" % (self.src, self.dst, self.dependents)
        # Select only those refs that are completely onscreen
        arrows = [ Arrow(src, dst)
                    for src, dst in arrows
                    if src in self.addr_line_map and dst in self.addr_line_map ]
        
        # build a DAG ordering inner to outer
        nodes = []
        for i in arrows:
            for j in nodes:
                # Add dependencies so shorter nodes are "inside" longer ones
                if i.begin >= j.begin and i.end <= j.end:
                    i.higher_arrows.append(j)
                    j.dependents += 1
                elif j.begin >= i.begin and j.end <= i.end:
                    j.higher_arrows.append(i)
                    i.dependents += 1
                # If neither arrow is within the other, create a dependency
                # from the one that starts first to the other
                elif j.begin < i.begin and j.end > i.begin:
                    j.higher_arrows.append(i)
                    i.dependents += 1
                elif i.begin < j.begin and i.end > j.begin:
                    i.higher_arrows.append(j)
                    j.dependents += 1

            nodes.append(i)

        # prepare the arrow list for layout/drawing
        queue = [a for a in nodes if a.dependents == 0]
        for i in queue:
            i.min_x = 67
        
        # Iterate one level of arrows at a time
        while queue:
            a = queue[0]
            queue = queue[1:]
            if a.drawn:
                continue
            
            if a.dependents:
                queue.append(a)
                continue

            try:
                selected_line = self.addr_line_map[self.memaddr_selected]
            except KeyError:
                selected_line = -1

            self.drawArrow(p, 
                a.min_x, 
                self.addr_line_map[a.src],
                self.addr_line_map[a.dst],
                selected_line)

            a.drawn = True

            for j in a.higher_arrows:
                j.min_x = min(a.min_x-12, j.min_x)
                j.dependents -= 1
                queue.append(j)


    def calculateLineParameters(self, data):
        lines_needed = 1
        disasm_start = 0
        label_start = 0

        if data.label:
            lines_needed += 2
            disasm_start += 2
            label_start = 1

        return lines_needed, disasm_start, label_start

    def calculateAddressLinecount(self, data):
        return calculateLineParameters(data)[0]

    def drawWidget(self, p):
        p.setFont(self.font)
        arrows = []
        
        self.line_addr_map = {}
        self.addr_line_map = {}
        
        # Calculate maximum number of lines on the screen
        nlines = self.geometry().height() / self.lineSpacing
        
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
            
            lines_needed, disasm_start, label_start = self.calculateLineParameters(line_data)


            label = line_data.label            
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
        
        self.drawArrows(p, arrows)



    def paintEvent(self, event):
        p = QtGui.QPainter()
        p.begin(self)
        # Wrap the actual paint code to prevent QT crashes
        # if we throw an exception
        try:
            self.drawWidget(p)
        finally:
            p.end()

