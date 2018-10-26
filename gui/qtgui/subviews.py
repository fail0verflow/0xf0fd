from symbolwidget import SymbolWidget
from consolewidget import ConsoleSubView
from subviewmgr import SubViewEntryBase

from PyQt5 import QtCore, QtGui, QtWidgets


class SymbolWidgetSubViewEntry(SubViewEntryBase):
    menuname = "Symbols"
    defaultArea = QtCore.Qt.LeftDockWidgetArea

    def __init__(self, subviewmgr, mainwindow):
        super(SymbolWidgetSubViewEntry, self).__init__(subviewmgr, mainwindow)

    # InstantiateWidget method called to create the actual widget to be
    # displayed. Connect widget with rest of UI
    def instantiateWidget(self):

        self._widget = SymbolWidget(self._mw, self._mw.datastore)

        self._widget.widget.symbolSelected.connect(
            self._mw.disassemblyWidget.navigateToIdentSL)

        self._widget.closed.connect(self.onClose)


class ConsoleWidgetSubViewEntry(SubViewEntryBase):
    menuname = "Console"
    defaultArea = QtCore.Qt.BottomDockWidgetArea

    def instantiateWidget(self):
        self._widget = ConsoleSubView(self._mw, self._mw.datastore)

        self._widget.closed.connect(self.onClose)
        self._widget.widget.actionOccurred.connect(
                self._mw.disassemblyWidget.update)
