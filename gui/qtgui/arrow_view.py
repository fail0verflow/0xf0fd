from PySide import QtGui, QtCore

STYLE_ARROW_FWD = 0x80004
STYLE_ARROW_BACK = 0x80005
STYLE_ARROW_SEL_FWD = 0x80006
STYLE_ARROW_SEL_BACK = 0x80007

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

        self.equiv_arrows = []

    def __str__(self):
        return "%04x -> %04x, [%d]" % (self.src, self.dst, self.dependents)





class FDArrowView(object):
    MAGIC_BEFOREWIN = -1
    MAGIC_AFTERWIN = -2

    def __init__(self, x, y, width, height, line_height):
        self.arrows_addrs = []
        self.line_height = line_height
        self.arrowEnd = 75
        self.selected_addr = None
        self.resize(width, height)

    def setSelectedAddr(self, addr):
        self.selected_addr = addr

    def applyStyle(self, p, styleType):
        #fwd_arrow_col       = QtGui.QColor(  0, 100,   0)
        #back_arrow_col      = QtGui.QColor(100,   0,   0)
        #fwd_sel_arrow_col   = QtGui.QColor(  0, 200,   0)
        #back_sel_arrow_col  = QtGui.QColor(200,   0,   0)
        fwd_arrow_col       = QtGui.QColor(200, 200, 200)
        back_arrow_col      = QtGui.QColor(200, 200, 200)
        fwd_sel_arrow_col   = QtGui.QColor(100, 100, 100)
        back_sel_arrow_col  = QtGui.QColor(100, 100, 100)

        stop_style          = QtGui.QColor(128,   0,   0)
        fg_col              = QtGui.QColor(  0,   0,   0)

        if styleType in [STYLE_ARROW_FWD, STYLE_ARROW_SEL_FWD, STYLE_ARROW_BACK, STYLE_ARROW_SEL_BACK]:
            colour = {
                        STYLE_ARROW_FWD: fwd_arrow_col,
                        STYLE_ARROW_BACK: back_arrow_col,
                        STYLE_ARROW_SEL_FWD: fwd_sel_arrow_col,
                        STYLE_ARROW_SEL_BACK: back_sel_arrow_col
                     }[styleType]

            width = {
                        STYLE_ARROW_FWD: 1,
                        STYLE_ARROW_SEL_FWD: 1,
                        STYLE_ARROW_BACK: 2,
                        STYLE_ARROW_SEL_BACK: 2
                    }[styleType]

            p.setBrush(colour)
            p.setPen(colour)
            pen = p.pen()
            pen.setWidth(width)
            p.setPen(pen)
        else:
            p.setBrush(fg_col)
            p.setPen(fg_col)
            p.setFont(self.font)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.nlines = self.height / self.line_height

    def clear(self):
        self.selected_addr = None
        self.arrows_addrs = []

    def addArrow(self, startAddr, endAddr):
        self.arrows_addrs.append( (startAddr, endAddr) )

    def drawArrow(self, p, col, startLine, endLine, selected):
        # Style the arrow based on direction, and whether a source or destination
        # are selected

        forward = endLine == self.MAGIC_AFTERWIN or endLine > startLine
        style = { (False, False): STYLE_ARROW_BACK,
                  (False, True):  STYLE_ARROW_SEL_BACK,
                  (True,  False): STYLE_ARROW_FWD,
                  (True,  True):  STYLE_ARROW_SEL_FWD }[forward, selected]
        self.applyStyle(p, style)

        draw_startMark = startLine >= 0
        draw_endMark = endLine >= 0
        
        if startLine == self.MAGIC_BEFOREWIN:
            startLine = 0
        elif startLine == self.MAGIC_AFTERWIN:
            startLine = self.nlines

        if endLine == self.MAGIC_BEFOREWIN:
            endLine = 0
        elif endLine == self.MAGIC_AFTERWIN:
            endLine = self.nlines

        # Calculate Y coordinates for the segments of the arrow
        asp = startLine * self.line_height + self.line_height/2
        aep = endLine * self.line_height + self.line_height/2

        # Start line
        if draw_startMark:
            p.drawLine(col, asp, self.arrowEnd, asp)

        # Shaft of arrow
        p.drawLine(col, asp, col, aep)

        if draw_endMark:
            # End Line
            p.drawLine(col, aep, self.arrowEnd, aep)

            # Draw the arrowhead
            p.drawLine(self.arrowEnd-3, aep-3, self.arrowEnd, aep)
            p.drawLine(self.arrowEnd-3, aep+3, self.arrowEnd, aep)


    def arrow_dir_same(self, a,b):
        if a.dst == a.src or b.dst == b.src:
            return True
        return ((a.dst - a.src) > 0) == ((b.dst - b.src) > 0)

    def render(self, p, addr_line_map):
        if not addr_line_map:
            return
        if not self.arrows_addrs:
            return

        # Select only those refs that are completely onscreen
        arrows = [ Arrow(src, dst)
                    for src, dst in self.arrows_addrs
                    ]
       
        # build a DAG ordering inner to outer
        nodes = []
        for i in arrows:
            skip_add_arrow = False

            for j in nodes:
                # Special case for merging arrows
                if i.dst == j.dst and self.arrow_dir_same(i,j):
                    i.equiv_arrows.append(j)
                    j.equiv_arrows.append(i)
                # Add dependencies so shorter nodes are "inside" longer ones                
                elif i.begin >= j.begin and i.end < j.end:
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
       
        min_addr = min(addr_line_map.keys())
        max_addr = max(addr_line_map.keys())
        
        # Iterate one level of arrows at a time
        while queue:
            a = queue[0]
            queue = queue[1:]
            if a.drawn:
                continue
            
            # If there are still dependant arrows to be drawn, defer drawing this arrow
            if a.dependents or any(map(lambda i: i.dependents > 0, a.equiv_arrows)):
                queue.append(a)
                queue.extend(a.equiv_arrows)
                continue

            selected = self.selected_addr in [a.src, a.dst]

            for arrow in [a] + a.equiv_arrows:
                skip_arrow = False

                try:
                    src_line = addr_line_map[arrow.src]
                except KeyError:
                    if arrow.src < min_addr:
                        src_line = self.MAGIC_BEFOREWIN
                    elif arrow.src > max_addr:
                        src_line = self.MAGIC_AFTERWIN
                    else:
                        skip_arrow = True


                try:
                    dst_line = addr_line_map[a.dst]
                except KeyError:
                    if arrow.dst < min_addr:
                        dst_line = self.MAGIC_BEFOREWIN
                    elif arrow.dst > max_addr:
                        dst_line = self.MAGIC_AFTERWIN
                    else:
                        skip_arrow = True

                if not skip_arrow:
                    self.drawArrow(p, 
                        arrow.min_x, 
                        src_line,
                        dst_line,
                        selected)

                arrow.drawn = True

                for j in arrow.higher_arrows:
                    j.min_x = min(arrow.min_x-12, j.min_x)
                    j.dependents -= 1
                    queue.append(j)
 
