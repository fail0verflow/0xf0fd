import sys
from PySide import QtCore, QtGui

from idis.datastore import DataStore
from arch.shared_opcode_types import *
from disassemblywidget import DisassemblyWidget
from symbolwidget import SymbolWidget

class MainWindow(QtGui.QMainWindow):
    def __init__(self, ds, filename):
        super(MainWindow, self).__init__()
        
        self.resize(800,600)
        self.setWindowTitle(filename)
        
        disassemblyWidget = DisassemblyWidget(self, ds)
        symbolWidget = SymbolWidget(self, ds)

        self.setCentralWidget(disassemblyWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, symbolWidget)

class QTGui(object):
    def __init__(self):
        pass

    def startup(self):
        pass

    def mainloop(self, filenames):
        if (len(filenames) < 1):
            print "usage: idis filename"
            sys.exit(-1)

        ds = DataStore(filenames[0])

        self.app = QtGui.QApplication(sys.argv)

        mainWin = MainWindow(ds, filenames[0])
        mainWin.show()

        self.app.exec_()


    def shutdown(self):
        pass

    def except_shutdown(self):
        self.app.exit()
