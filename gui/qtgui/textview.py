from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import math


class FDTextAttribs(object):
    def __init__(self,
            color=None,
            bgcolor=None,
            isBold=False,
            isItalic=False):

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
    def __init__(self, x, y, width, height,
            bgcolor=QColor(255, 255, 255),
            fgcolor=QColor(0, 0, 0)):

        self.font_family = "courier"
        self.font = QFont(self.font_family)
        self.font.setFixedPitch(True)
        self.font.setKerning(False)
        self.font.setStyleHint(QFont.Courier, QFont.PreferBitmap)

        self.font_bold = QFont(self.font_family, weight=75)
        self.font_bold.setFixedPitch(True)
        self.font.setKerning(False)
        self.font.setStyleHint(QFont.Courier, QFont.PreferBitmap)

        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.x_0 = x
        self.y_0 = y

        self.setupFontParams()

        self.resize(width, height)
        self.clear()

    def mixColors(self, a, b):
        dfw_r = 255 - a.red()
        dfw_g = 255 - a.green()
        dfw_b = 255 - a.blue()

        new_r = max(b.red() - dfw_r, 0)
        new_b = max(b.blue() - dfw_g, 0)
        new_g = max(b.green() - dfw_b, 0)

        return QColor(new_r, new_g, new_b)

    def mapCoords(self, x, y):
        """ Returns line, character_pos, tag [if present] """
        line = int((y - self.y_0) / self.c_height)
        char = int((x - self.x_0) / self.c_width)

        try:
            row = self.row_map[line]

        except KeyError:
            return None, None, None

        try:
            block = [i for i in row
                     if i.col <= char and (i.col + len(i.text)) > char][0]
            tag = block.tag
        except IndexError:
            tag = None

        return line, char, tag

    def resize(self, width, height):
        self.width = width
        self.height = height

        self.nlines = math.ceil(self.height / float(self.c_height))

    def clear(self):
        self.row_map = {}
        self.row_highlights = {}

    def setRowHighlight(self, row, color):
        self.row_highlights[row] = color

    def addText(self, row, col, text, attribs, tag=None):
        self.attribs = attribs
        try:
            row_o = self.row_map[row]
        except KeyError:
            row_o = self.row_map[row] = []

        row_o.append(FDTextBlock(col, text, attribs, tag))

        row_o.sort(lambda a, b: cmp(a.col, b.col))

    def setupFontParams(self):
        metrics = QFontMetricsF(self.font)

        self.c_height = metrics.height()
        self.c_baseline = metrics.ascent()

        # Ugly hack - QFontMetricsF(font) gives us wrong values
        #  but since we can only get Integer font metrics on
        #  a QPainter, we need to average it from a long string
        #
        # For now, in testing this fixes issues on Mac OS X
        # Need to check to make sure this doesn't break on Linux/Win
        pix = QPixmap(64, 64)
        painter = QPainter()
        painter.begin(pix)
        painter.setFont(self.font)
        self.c_width = painter.fontMetrics().width("helloworld" * 64) / 640.0
        painter.end()

    def drawArea(self, p):
        bg_brush = QBrush(self.bgcolor)

        geom = QRect(self.x_0, self.y_0, self.width, self.height)
        p.fillRect(geom, bg_brush)

        for row, blocks in self.row_map.iteritems():
            row_top_y = self.y_0 + self.c_height * row
            row_bot_y = self.y_0 + self.c_height * (row + 1)
            row_baseline_y = self.y_0 + self.c_height * row + self.c_baseline

            try:
                p.fillRect(self.x_0, row_top_y,
                           self.width, self.c_height,
                           self.row_highlights[row])

            except KeyError:
                pass

            blocks.sort(lambda a, b: cmp(a.col, b.col))

            lastcol = 0

            for block in blocks:
                attribs = block.attribs

                st_col = max(block.col, lastcol)

                # Insert an extra column when we had overlapping blocks
                # Overlapping text blocks are never an intentional input
                # condition. When they occur, something was configured wrong
                # and rendering usually looks best with space before the next
                # char
                if st_col > block.col:
                    st_col += 1

                block_start_x = self.x_0 + self.c_width * st_col
                block_end_x = self.x_0 + self.c_width * (
                    st_col + len(block.text))

                lastcol = max(st_col + len(block.text), st_col)

                block_width = self.c_width * len(block.text)

                p.setFont(self.font)

                bgcolor = self.bgcolor
                fgcolor = self.fgcolor

                if attribs:
                    bgcolor = attribs.bgcolor if \
                        attribs.bgcolor else self.bgcolor
                    fgcolor = attribs.color if attribs.color else self.fgcolor

                    try:
                        p.fillRect(QRect(block_start_x, row_top_y,
                            block_width, self.c_height),
                            self.mixColors(bgcolor, self.row_highlights[row]))

                    except KeyError:
                        if bgcolor != self.bgcolor:
                            p.fillRect(QRect(block_start_x, row_top_y,
                                block_width, self.c_height), bgcolor)

                    if attribs.isBold:
                        p.setFont(self.font_bold)

                p.setPen(fgcolor)
                p.drawText(block_start_x, row_baseline_y, block.text)
