import time

from PySide import QtCore, QtGui
from arch.shared_opcode_types import *

# TODO: Removeme
from arch.common.hacks import *

from datastore import CommentPosition, InfoStore
from textview import FDTextArea, FDTextAttribs
from arrow_view import FDArrowView

STYLE_HEXADDR = 0x80001
STYLE_COMMENT = 0x80002
STYLE_OPCODE = 0x80003
STYLE_DIVIDER = 0x80008
STYLE_INTERNALERROR = 0x80009
STYLE_XREF = 0x8000A

TA = FDTextAttribs


class DisassemblyGraphicsView(QtGui.QWidget):
    def __init__(self, ds, mapper):
        QtGui.QWidget.__init__(self)

        self.addrX = 0
        self.labelX = 18
        self.xrefX = 50
        self.disasmX = 20
        self.firstOpcodeX = 31
        self.commentX = 56

        self.sel_color = QtGui.QColor(190, 190, 255)

        self.ds = ds
        self.resize(800, 600)

        self.memaddr_top = 0
        self.memaddr_selected = 0

        # Used for calculating clicks
        self.line_addr_map = {}

        # Used for drawing arrows
        self.addr_line_map = {}

        # Used for line highlighting - tuple of first,
        # last line that is at that address
        self.highlight_addr_range = {}

        self.arrowWidth = 80

        self.atv = FDTextArea(
            self.arrowWidth, 0,
            self.width() - self.arrowWidth,
            self.height())

        self.arv = FDArrowView(0, 0,
            self.arrowWidth, self.height(),
            self.atv.c_height)

        self.setSizes()

    def setSizes(self):
        self.atv.resize(self.width() - self.arrowWidth, self.height())
        self.arv.resize(self.arrowWidth, self.height())

    def getClickAddr(self, x, y):
        lineIndex, char, tag = self.atv.mapCoords(x, y)

        if lineIndex == None:
            return None

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
        symbolic_col = QtGui.QColor(0, 200, 0)
        fg_col = QtGui.QColor(0, 0, 0)
        comment_col = QtGui.QColor(127, 127, 127)
        opcode_col = QtGui.QColor(0, 0, 127)
        xref_col = QtGui.QColor(80, 80, 187)
        divider_col = QtGui.QColor(180, 180, 180)

        if styleType == TYPE_SYMBOLIC:
            return TA(color=symbolic_col, isBold=True)

        elif styleType == STYLE_COMMENT:
            return TA(color=comment_col)

        elif styleType == STYLE_XREF:
            return TA(color=xref_col)

        elif styleType == STYLE_OPCODE:
            return TA(color=opcode_col)

        elif styleType == STYLE_DIVIDER:
            return TA(color=divider_col)

        elif styleType == STYLE_INTERNALERROR:
            return TA(color=QtGui.QColor(255, 0, 0))

        else:
            return TA(color=fg_col)

    def mapDest(self, segment, d):
        try:
            return segment.mapOut(d)
        except ValueError:
            return None

    def calculateLineParameters(self, data):
        lines_needed = 1
        disasm_start = 0
        label_start = 0
        divider_start = None

        n_max_xrefs = 3

        n_xref_lines = min(n_max_xrefs,
                len(self.ds.xreflist.getXrefsTo(data.addr)))

        lines_needed += n_xref_lines
        disasm_start += n_xref_lines
        label_start += n_xref_lines

        if data.label:
            lines_needed += 2
            disasm_start += 2
            label_start += 1

        try:
            # Calculate dest idents
            segment = self.ds.segments.findSegment(data.addr)
            dests = [
                (self.mapDest(segment, i), j)
                for i, j in data.disasm.dests()]

            # Space for a divider if code execution completes
            if data.addr + data.length not in [i for i, _ in dests]:
                lines_needed += 2
                divider_start = disasm_start + 1

        except AttributeError:
            pass

        return (lines_needed, disasm_start, label_start, divider_start,
                    n_xref_lines)

    def calculateAddressLinecount(self, data):
        return calculateLineParameters(data)[0]

    # Perform mock layout to calculate last fully drawn addr
    def calculateLastFullyDrawnAddr(self, start=None):

        line_ident = start if start else self.memaddr_top

        nlines = self.atv.nlines
        i = 0

        lastDrawnAddr = None

        # NOTE: Keep in sync with draw routine below; or create line
        # orientation generator
        while i < nlines:
            rc, line_data = self.ds.infostore.lookup(line_ident)

            if rc != InfoStore.LKUP_OK:
                line_ident += 1
                i += 1
                continue

            (lines_needed, disasm_start, label_start,
                    divider_start, n_xref_lines) = \
                self.calculateLineParameters(line_data)

            i += lines_needed
            if i < nlines:
                lastDrawnAddr = line_ident

            line_ident += line_data.length

        return lastDrawnAddr

    def drawWidget(self, p):
        self.atv.clear()
        self.arv.clear()

        self.line_addr_map = {}
        self.addr_line_map = {}
        self.highlight_addr_range = {}

        # Calculate maximum number of lines on the screen
        nlines = self.atv.nlines

        # Erase the widget
        bg_brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        p.fillRect(self.geometry(), bg_brush)

        # line marker background
        ln_brush1 = QtGui.QColor(250, 250, 255)

        # selected line background
        sel_line = QtGui.QColor(200, 200, 255)

        line_ident = self.memaddr_top

        i = 0
        i_mod = 0
        while i < nlines:

            segment = self.ds.segments.findSegment(line_ident)

            # Fix bug when there are no segments created
            if not segment:
                break

            rc, line_data = self.ds.infostore.lookup(line_ident)

            if rc != InfoStore.LKUP_OK:
                line_segaddr = segment.mapIn(line_ident)
                line_segname = segment.name + ":" if line_seg.name else ""

                self.atv.addText(i, self.addrX,
                    "%s%08x:" % (line_segname, line_segaddr),
                    self.getStyle(STYLE_INTERNALERROR))

                self.atv.addText(
                    i,
                    self.disasmX,
                    "<err - couldn't lookup, but in segment!>",
                    self.getStyle(STYLE_INTERNALERROR))

                line_ident += 1
                i += 1
                continue

            try:
                dests = [
                    (self.mapDest(segment, i_), i_, j)
                    for i_, j in line_data.disasm.dests()
                    ]

            # In case "dests" is not implemented
            except AttributeError:
                dests = []

            #
            # layout is:
            #   0001
            #   0001   label:
            #   0001       opcode
            #   0002
            #
            #
            (lines_needed, disasm_start, label_start,
                    divider_start, n_xref_lines) = \
                self.calculateLineParameters(line_data)
            label = line_data.label

            # Draw the xrefs
            xrefs = self.ds.xreflist.getXrefsTo(line_data.addr)

            xreflbl = "Xrefs: "
            for xi in xrange(0, n_xref_lines):

                # Lookup the xref source to get a name
                _, dxr = self.ds.infostore.lookup(xrefs[xi].ident_from)
                xreftext = None  # dxr.label

                if not xreftext:
                    dxrseg = self.ds.segments.findSegment(dxr.addr)
                    if not dxrseg:
                        xreftext = "%x" % dxr.addr
                    else:
                        if dxrseg.name:
                            xreftext = "%s:%x" % (dxrseg.name,
                                dxrseg.mapIn(dxr.addr))
                        else:
                            xreftext = "%x" % dxrseg.mapIn(dxr.addr)

                if xi != 0:
                    self.atv.addText(
                        i + xi + 1,
                        self.xrefX + len(xreflbl),
                        xreftext,
                        self.getStyle(STYLE_XREF))
                else:
                    self.atv.addText(
                        i + xi + 1,
                        self.xrefX,
                        xreflbl + xreftext,
                        self.getStyle(STYLE_XREF))

            # draw the label [if any]
            if label:
                self.atv.addText(
                    i + label_start,
                    self.labelX,
                    "%s:" % label,
                    self.getStyle(TYPE_SYMBOLIC))

            opcode = line_data.disasm.mnemonic

            # Draw addresses
            for indiv_line in xrange(lines_needed):
                self.line_addr_map[indiv_line + i] = line_ident
                line_seg = segment
                line_segaddr = line_seg.mapIn(line_ident)
                line_segname = line_seg.name + ":" if line_seg.name else ""
                self.atv.addText(indiv_line + i, self.addrX,
                    "%s%08x:" % (line_segname, line_segaddr),
                    self.getStyle(STYLE_HEXADDR))

            # Draw opcode
            self.atv.addText(
                i + disasm_start,
                self.disasmX,
                "%s" % opcode,
                self.getStyle(STYLE_OPCODE))

            self.addr_line_map[line_ident] = disasm_start + i

            # Calculate a range that covers the actual range that has displayed
            # content for highlighting purposes
            line_end = i + lines_needed

            if divider_start:
                line_end = i + divider_start

            self.highlight_addr_range[line_ident] = (i + label_start,
                line_end)

            # Add addr to disasm
            try:
                for arrow in [
                            (line_data.addr, dest_ident)
                            for dest_ident, dest_addr, desttype in dests
                            if (dest_ident != line_data.addr + line_data.length
                                and desttype == REL_JUMP)]:
                    self.arv.addArrow(arrow[0], arrow[1])

            except AttributeError:
                pass

            # Draw destination
            opcodeX = self.firstOpcodeX
            for opcode_num in xrange(len(line_data.disasm.operands)):
                operand = line_data.disasm.operands[opcode_num]
                last_operand = opcode_num == len(line_data.disasm.operands) - 1

                text, opc_type = operand.render(self.ds, segment)

                opcode_text = text
                self.atv.addText(i + disasm_start,
                    opcodeX, opcode_text,
                    self.getStyle(opc_type), opcode_text)

                opcodeX += len(opcode_text)

                # Draw the ", " separator
                if not last_operand:
                    separator = ", "
                    self.atv.addText(i + disasm_start, opcodeX,
                        separator, None)
                    opcodeX += len(separator)

            # Draw comment
            comment = self.ds.comments.getCommentText(
                line_ident, CommentPosition.POSITION_RIGHT)

            if comment:
                self.atv.addText(
                    i + disasm_start,
                    self.commentX,
                    "; %s" % comment,
                    self.getStyle(STYLE_COMMENT))

            # Draw divider
            if divider_start != None:
                self.atv.addText(
                    i + divider_start,
                    self.disasmX,
                    "-" * 60,
                    self.getStyle(STYLE_DIVIDER))

            i += lines_needed
            if i < nlines:
                self.lastDrawnAddr = line_ident

            line_ident += line_data.length
            i_mod += 1

        try:
            selection_line = self.highlight_addr_range[self.memaddr_selected]
        except KeyError:
            pass
        else:
            for line_i in xrange(selection_line[0], selection_line[1]):
                self.atv.setRowHighlight(line_i, self.sel_color)

        self.arv.setSelectedAddr(self.memaddr_selected)

        # Render [and time] the text and arrow areas
        time_rendering = False

        if time_rendering:
            render_start = time.time()

        self.atv.drawArea(p)

        if time_rendering:
            render_text = time.time()

        self.arv.render(p, self.addr_line_map)

        if time_rendering:
            render_end = time.time()
            print "Frame render time: %f %f" % (
                render_text - render_start, render_end - render_text)

    def paintEvent(self, event):
        time_paintEvents = False

        if time_paintEvents:
            start = time.time()

        p = QtGui.QPainter()
        p.begin(self)
        # Wrap the actual paint code to prevent QT crashes
        # if we throw an exception
        try:
            self.drawWidget(p)
        finally:
            p.end()

        if time_paintEvents:
            end = time.time()
            print end - start
