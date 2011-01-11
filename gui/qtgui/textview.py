from PySide.QtCore import *
from PySide.QtGui import *
import math

class FDTextAttribs(object):
    def __init__(self, 
        color=QColor(0,0,0), 
        bgcolor=QColor(255,255,255),
        isBold = False,
        isItalic = False,
            ):
        self.color = color
        self.bgcolor = bgcolor
        self.isBold = isBold
        self.isItalic = isItalic

class FDTextBlock(object):
    def __init__(self, start, text, attribs, tag):
        self.col = start
        self.text = text
        self.attribs = attribs
        self.tag = tag

#
# Textview, rows/cols numbered:
#     0123
#     _____
# 0  |
# 1  |
# 2  |
#
#

class FDTextArea(object):
    def __init__(self, x,y,width, height):
        self.row_map = {}
        
        self.font_family = "courier"
        self.font = QFont(self.font_family)
        self.font_bold = QFont(self.font_family, weight=75)
        self.bgcolor = QColor(255,255,255)
        self.fgcolor = QColor(0,0,0)
        self.sel_color = QColor(190, 190, 255)
        self.x_0 = x
        self.y_0 = y
    
        self.resize(width, height)

        self.selectedLine = None

    def mixColors(self, a, b):
        dfw_r = 255 - a.red()
        dfw_g = 255 - a.green()
        dfw_b = 255 - a.blue()

        new_r = max(b.red()-dfw_r, 0)
        new_b = max(b.blue()-dfw_g, 0)
        new_g = max(b.green()-dfw_b, 0)

        return QColor(new_r, new_g, new_b)

    
    def setSelectedLine(self, line):
        self.selectedLine = line

    def resize(self, width, height):
        self.width = width
        self.height = height


    def clear(self):
        self.row_map = {}

    def addText(self, row, col, text, attribs, tag=None):
        self.attribs = attribs
        try:
            row_o = self.row_map[row]
        except KeyError:
            row_o = self.row_map[row] = []
        
        row_o.append(FDTextBlock(col, text, attribs, tag))

        row_o.sort(lambda a,b: cmp(a.col, b.col))

    def setupFontParams(self, p):
        p.setFont(self.font)
        metrics = p.fontMetrics()

        self.c_width = metrics.width(' ')
        self.c_height = metrics.height()
        self.c_baseline = metrics.ascent()
       
        self.nlines = math.ceil(self.height / float(self.c_height))

    def drawArea(self, p):
        self.setupFontParams(p)

        bg_brush = QBrush(self.bgcolor)

        geom = QRect(self.x_0, self.y_0, self.width, self.height)
        p.fillRect(geom, bg_brush)

        for row, blocks in self.row_map.iteritems():
            row_top_y = self.y_0 + self.c_height * row
            row_bot_y = self.y_0 + self.c_height * (row + 1)
            row_baseline_y = self.y_0 + self.c_height * row + self.c_baseline

            if self.selectedLine == row:
                p.fillRect(self.x_0, row_top_y, self.width, self.c_height, self.sel_color)

            for block in blocks:
                attribs = block.attribs
                block_start_x = self.x_0 + self.c_width * block.col
                block_end_x = self.x_0 + self.c_width * (block.col + len(block.text))
                block_width = self.c_width * len(block.text)

                p.setPen(self.fgcolor)
                p.setFont(self.font)

                if attribs:
                    if self.selectedLine == row:
                        p.fillRect(QRect(block_start_x, row_top_y, 
                            block_width, self.c_height), self.mixColors(attribs.bgcolor, self.sel_color))
                    else:
                        p.fillRect(QRect(block_start_x, row_top_y, 
                            block_width, self.c_height), attribs.bgcolor)

                        
                    p.setPen(attribs.color)
                    if attribs.isBold:
                        p.setFont(self.font_bold)


                p.drawText(block_start_x, row_baseline_y, block.text)

