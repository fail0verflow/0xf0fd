from PySide import QtCore, QtGui


class TreeItem(object):
    def __init__(self, key, value, parent=None):
        self.key = key
        self.value = value
        self.parent = parent
        self.children = []
        self.index = None
        self.row = 0
        
    def addChild(self, treeitem):
        self.children += [treeitem]
        treeitem.row = len(self.children) - 1
        treeitem.parent = self
    
    def childCount(self):
        return len(self.children)
        
    def data(self, col):
        if col == 0:
            return self.key
        return self.value
        
class InspectModel(QtCore.QAbstractItemModel):
    def __init__(self, info):
        super(InspectModel, self).__init__()
        
        self.root = TreeItem("root","")
        
        self.root.addChild(TreeItem("addr", "%04x" % info.addr))
        self.root.addChild(TreeItem("length", "%d" % info.length))
        
        self.root.addChild(TreeItem("label", "%s" % info.label))
        self.root.addChild(TreeItem("comment", "%s" % info.comment))
        
        def dumpDict(node, dct):
            for k,v in dct.iteritems():
                if hasattr(v, "iteritems"):
                    childNode = TreeItem(k, "")
                    dumpDict(childNode, v)
                else:
                    childNode = TreeItem(k, str(v))
                node.addChild(childNode)
                
            return node
        # show cdict, disasm, persist_attribs
        self.root.addChild(dumpDict(TreeItem("cdict",""), info.cdict))
        self.root.addChild(TreeItem("disasm",str(info.disasm)))
        self.root.addChild(dumpDict(TreeItem("persist_attribs",""), info.persist_attribs))
        
    def columnCount(self, index):
        return 2
    
    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()
        
        return parentItem.childCount()
        
    def index(self, row, col, parent):
        if not self.hasIndex(row, col, parent):
            return QtCore.QModelIndex()


        if not parent.isValid():
            parentItem = self.root
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.children[row]
        
        if childItem is not None:
            return self.createIndex(row, col, childItem)
        else:
            return QtCore.QModelIndex()

        
    def data(self, index, role):
        if not index.isValid(): return None
        if role != QtCore.Qt.DisplayRole: return None
        
        return index.internalPointer().data(index.column())
        
    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent
        if parentItem is None:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentItem.row, 0, parentItem)
            
class InspectWidget(QtGui.QWidget):
    def __init__(self, info):
        super(InspectWidget, self).__init__()
        self.treeview = QtGui.QTreeView()
        self.model = InspectModel(info)
        self.treeview.setModel(self.model)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.treeview)
        self.setWindowTitle("Inspector for %04x" % info.addr)
        self.setLayout(mainLayout)
        self.resize(600,400)
        self.treeview.setColumnWidth(0,200)

class InspectWindow(QtGui.QDockWidget):
    def __init__(self, info):
        super(InspectWindow, self).__init__("Inspector")
        self.widget = InspectWidget(info)
        self.setWidget(self.widget)
