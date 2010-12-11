import sys
from PySide import QtCore, QtGui

from idis.datastore import DataStore
from arch.shared_opcode_types import *
from disassemblywidget import DisassemblyWidget

class MainWindow(QtGui.QWidget):
    def __init__(self, ds, filename):
        super(MainWindow, self).__init__()
        
        self.resize(800,600)
        self.setWindowTitle(filename)
        
        disassemblyWidget = DisassemblyWidget(self, ds)
        
        view = DisassemblyWidget(self, ds)
        
        mainLayout = QtGui.QHBoxLayout()

        mainLayout.addWidget(disassemblyWidget)
        
        self.setLayout(mainLayout)



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

        app = QtGui.QApplication(sys.argv)

        mainWin = MainWindow(ds, filenames[0])
        mainWin.show()

        app.exec_()


    def shutdown(self):
        pass


