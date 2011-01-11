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

    def __str__(self):
        return "%04x -> %04x, [%d]" % (self.src, self.dst, self.dependents)





class FDArrowView(object):
    def __init__(self, x, y, width, height, line_height):
        self.resize(width, height)
        self.arrows_addrs = []
        self.line_height = line_height
        self.arrowEnd = 75


    def applyStyle(self, p, styleType):
        fwd_arrow_col       = QtGui.QColor(  0, 100,   0)
        back_arrow_col      = QtGui.QColor(100,   0,   0)
        fwd_sel_arrow_col   = QtGui.QColor(  0, 200,   0)
        back_sel_arrow_col  = QtGui.QColor(200,   0,   0)
        fg_col              = QtGui.QColor(  0,   0,   0)

        if styleType in [STYLE_ARROW_FWD, STYLE_ARROW_SEL_FWD, STYLE_ARROW_BACK, STYLE_ARROW_SEL_BACK]:
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

    def resize(self, width, height):
        self.width = width
        self.height = height

    def clear(self):
        self.arrows_addrs = []

    def addArrow(self, startAddr, endAddr):
        self.arrows_addrs.append( (startAddr, endAddr) )

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
        asp = startLine * self.line_height + self.line_height/2
        aep = endLine * self.line_height + self.line_height/2

        p.drawLine(col, asp, self.arrowEnd, asp)
        p.drawLine(col, asp, col, aep)
        p.drawLine(col, aep, self.arrowEnd, aep)

        # Draw the arrowhead
        p.drawLine(self.arrowEnd-3, aep-3, self.arrowEnd, aep)
        p.drawLine(self.arrowEnd-3, aep+3, self.arrowEnd, aep)


    def render(self, p, addr_line_map):
        # Select only those refs that are completely onscreen
        arrows = [ Arrow(src, dst)
                    for src, dst in self.arrows_addrs
                    if src in addr_line_map and dst in addr_line_map ]
       
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
            
            # If there are still dependant arrows to be drawn, defer drawing this arrow
            if a.dependents:
                queue.append(a)
                continue

            # Map the selected address to a line onscreen
            #try:
            #    selected_line = addr_line_map[self.memaddr_selected]
            #except KeyError:
            selected_line = -1

            self.drawArrow(p, 
                a.min_x, 
                addr_line_map[a.src],
                addr_line_map[a.dst],
                selected_line)

            a.drawn = True

            for j in a.higher_arrows:
                j.min_x = min(a.min_x-12, j.min_x)
                j.dependents -= 1
                queue.append(j)
 
