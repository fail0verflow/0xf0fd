from PySide import QtGui, QtCore


class SubViewManager(object):

    def __init__(self, mainwin):
        self.__mw = mainwin

        self.svl = [i(self, self.__mw) for i in SubViewBase.__subclasses__()]

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


class SubViewBase(object):
    def __init__(self, svm, mw):
        self._svm = svm
        self._mw = mw
        self.vis = False
        self.area = self.defaultArea

    def initialSetup(self, action):
        self._a = action
        self.show()

    def doMenuSelect(self):
        if self.vis:
            self.hide()
        else:
            self.show()

        self._a.setChecked(self.vis)

    def onClose(self):
        self.vis = False
        del self._widget
        self._a.setChecked(self.vis)

    def show(self):
        if self.vis:
            return

        self.vis = True

        self.instantiateWidget()

        self._mw.addDockWidget(self.area,
                self._widget)

        self._a.setChecked(True)

    def hide(self):
        if not self.vis:
            return

        self._widget.close()
        # onClose Event handler will fire and update state
