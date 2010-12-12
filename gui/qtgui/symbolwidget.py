from PySide import QtCore, QtGui

class SymbolModel(QtCore.QAbstractItemModel):
    def __init__(self, ds):
        super(SymbolModel, self).__init__()
        self.datastore = ds
        self.order_dir = 'ASC'
        self.order = 'addr'

    def sort(self, col_num, order):
        assert col_num in [0,1]
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        
        self.order = { 0: 'name',
                       1: 'addr' }[col_num]

        self.order_dir = {
                       QtCore.Qt.AscendingOrder: 'ASC',
                       QtCore.Qt.DescendingOrder:'DESC'}[order]

        self.emit(QtCore.SIGNAL("layoutChanged()"))


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "Name"
                else:
                    return "Addr"

        return None

    def columnCount(self, parent):
        return 2
    
    def rowCount(self, parent):
        if parent.isValid():
            return 0

        return len(self.datastore.symbols)

    def index(self, row, col, parent):
        if parent.isValid():
            return QtCore.QQModelIndex()

        addr, name = self.datastore.symbols.listInterface(self.order, self.order_dir, row)
        return self.createIndex(row, col, addr)

    def parent(self, index):
        return QtCore.QModelIndex()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            addr, name = self.datastore.symbols.listInterface(self.order, self.order_dir, index.row())
            if index.column() == 1:
                return "%x" % addr
            return name
        return None


class SymbolTableView(QtGui.QTableView):
    def __init__(self, parent_win, ds):
        super(SymbolTableView, self).__init__()

        self.model = SymbolModel(ds)

        self.setModel(self.model)
        self.setShowGrid(False)

        self.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.setSortingEnabled(True)
       
        # TODO: pull section height and font from config
        vh = self.verticalHeader()
        vh.setVisible(False)
        vh.setDefaultSectionSize(15)

        font = QtGui.QFont("Courier New", 12)
        self.setFont(font)

        # Highlight only on a per-row basis
        hh = self.horizontalHeader()
        hh.setHighlightSections(False)

        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

class SymbolWidget(QtGui.QDockWidget):
    def __init__(self, parent_win, ds):
        super(SymbolWidget, self).__init__("Symbols", parent_win)
        
        self.widget = SymbolTableView(self, ds)
        self.setWidget(self.widget)
