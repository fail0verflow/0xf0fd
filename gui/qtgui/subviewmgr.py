from PySide import QtGui, QtCore

from symbolwidget import SymbolWidget


class SymbolWidgetSubViewEntry(object):
    menuname = "Symbols"

    def __init__(self, svm, mw):
        self.__mw = mw
        self.__svm = svm
        self.vis = False

    def initialSetup(self, action):
        self.__a = action
        self.show()

    def doMenuSelect(self):
        if self.vis:
            self.hide()
        else:
            self.show()
        self.__a.setChecked(self.vis)

    def onClose(self):
        self.vis = False
        del self.symbolWidget
        self.__a.setChecked(self.vis)

    def show(self):
        if self.vis:
            return

        self.vis = True
        self.symbolWidget = SymbolWidget(self.__mw, self.__mw.datastore)

        self.symbolWidget.widget.symbolSelected.connect(
            self.__mw.disassemblyWidget.gotoIdentSL)

        self.__mw.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                self.symbolWidget)

        self.symbolWidget.closed.connect(self.onClose)
        self.__a.setChecked(True)

    def hide(self):
        if not self.vis:
            return

        self.symbolWidget.close()
        # onClose Event handler will fire and update state


class SubViewManager(object):
    svlc = [
            SymbolWidgetSubViewEntry,
            ]

    def __init__(self, mainwin):
        self.__mw = mainwin

        self.svl = [i(self, self.__mw) for i in self.svlc]

        self.viewmenu = QtGui.QMenu("View", self.__mw)

        for ins in self.svl:
            a = self.viewmenu.addAction(QtGui.QIcon(), ins.menuname,
                    ins.doMenuSelect, "doSelectMenu")
            a.setCheckable(True)

            ins.initialSetup(a)

        self.viewmenu.addSeparator()
        self.viewmenu.addAction("Reset View", self.reset)

        self.__mw.menuBar().addMenu(self.viewmenu)

    def reset(self):
        for i in self.svl:
            i.hide()
            i.show()
