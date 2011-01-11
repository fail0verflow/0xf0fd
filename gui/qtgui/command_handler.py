

import idis.tools
import idis.tools_algos
import arch

from idis.cmd.command import *
from idis.dbtypes import CommentPosition
from inspect import InspectWindow

from PySide import QtCore
from PySide import QtGui

keyList = dict([(getattr(QtCore.Qt, key), key) for key in dir(QtCore.Qt) if key.startswith('Key')])


class AddCommentWindow(QtGui.QDialog):
    def __init__(self, position, oldcomment):
        super(AddCommentWindow, self).__init__()

        positionText = {
            CommentPosition.POSITION_BEFORE: "Pre-line comment",
            CommentPosition.POSITION_RIGHT:  "Line comment",
            CommentPosition.POSITION_BOTTOM: "Post-line comment"
            }[position]

        okButton = QtGui.QPushButton("OK")
        okButton.setDefault(True)
        QtCore.QObject.connect(okButton, QtCore.SIGNAL('clicked()'), self.accept)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtGui.QDialogButtonBox.ActionRole)

        self.formLayout = QtGui.QFormLayout()
        self.positionLabel = QtGui.QLabel(positionText)
        self.edit = QtGui.QTextEdit(oldcomment)
        
        self.formLayout.addRow("&Position:", self.positionLabel)
        self.formLayout.addRow("&Comment text:", self.edit)

        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

class AddBinaryPromptWindow(QtGui.QDialog):
    def __init__(self):
        super(AddBinaryPromptWindow, self).__init__()
        
        # Todo - make validator that changes background red for bad values
        # and disables okButton 
        
        # TODO: add cancel button
        
        # TODO: remove close and make act like a normal dialog
        okButton = QtGui.QPushButton("OK")
        okButton.setDefault(True)
        QtCore.QObject.connect(okButton, QtCore.SIGNAL('clicked()'), self.accept)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(okButton, QtGui.QDialogButtonBox.ActionRole)

        self.formLayout = QtGui.QFormLayout()
        self.baseEdit = QtGui.QLineEdit("0x0")
        self.startEdit = QtGui.QLineEdit("0x0")
        self.lengthEdit = QtGui.QLineEdit("-1")
        self.formLayout.addRow("&Base Address:", self.baseEdit)
        self.formLayout.addRow("&Start Offset:", self.startEdit)
        self.formLayout.addRow("&Length:", self.lengthEdit)
        self.formLayout.addWidget(buttonBox)
        self.setLayout(self.formLayout)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        

class CommandHandler(object):

    def handleSetStdComment(self, ident, pos=CommentPosition.POSITION_RIGHT):
        oldcomment = self.ds.comments.getCommentText(ident, pos)

        cw = AddCommentWindow(pos, oldcomment)
        cw.exec_()
        self.ds.cmdlist.push(CommentCommand(ident, pos, cw.edit.toPlainText()))


    def handleAddBinary(self, addr):
        # FIXME: use command pattern
        filename, filter = QtGui.QFileDialog.getOpenFileName()
        bpw = AddBinaryPromptWindow()
        bpw.exec_()
        base_addr = int(bpw.baseEdit.text(),0)
        start_offset = int(bpw.startEdit.text(),0)
        length = int(bpw.lengthEdit.text(),0)
        idis.tools_loaders.addBinary(self.ds, filename, base_addr, start_offset, length)
        
        
    def handleInspect(self, addr):
        info = self.ds[addr]
        iw = InspectWindow(info)
        iw.show()
        self.iws += [iw]
        
    def handleSetLabel(self, addr):
        oldlabel = self.ds[addr].label
        text, ok = QtGui.QInputDialog.getText(None, "Set Label", "Enter a label for addr %04x" % addr, text=oldlabel)
        if ok and text != oldlabel:
            self.ds.cmdlist.push(SymbolNameCommand(addr, text))

    def handleCodeFollow(self, addr):
        # FIXME: use command pattern [super object]
        a = self.gui.global_archname
        idis.tools_algos.codeFollow(self.ds, a, addr)

    def handleFollowJump(self, addr):
        newaddr = idis.tools.follow(self.ds, addr)
        try:
            self.ds[newaddr]
            self.memstack.append((self.view.view.getTopAddr(), self.view.view.getSelAddr()))
                
            self.view.gotoAddress(newaddr)
                
        except KeyError:
            pass

    def handleCodeReturn(self, addr):
        try:
            top,sel = self.memstack.pop()
        except IndexError:
            return
        
        self.view.gotoAddress(sel, top)
    
    def buildCmdHandlers(self, pairs):
        """ call with a set of pairs such as: 
            [ ( "Semicolon", "AddBinary" ) ] """

        self.cmd_handlers = dict([
            (getattr(QtCore.Qt, "Key_%s" % a), getattr(self, "handle%s" % b))
                for a, b in pairs
            ])


    def __init__(self, gui, ds, view):
        self.gui = gui
        self.iws = []
        self.ds = ds
        self.memstack = []
        self.view = view

        handlers = [
            ("A", "AddBinary"),
            ("I", "Inspect"),
            ("C", "CodeFollow"),
            ("Return", "FollowJump"),
            ("N", "SetLabel"),
            ("Backspace", "CodeReturn"),
            ("Escape", "CodeReturn"),
            ("Semicolon", "SetStdComment")
            ]

        self.buildCmdHandlers(handlers)
        
    def handleCommand(self, addr, cmd):
        try:
            self.cmd_handlers[cmd](addr)
        except KeyError:
            print keyList[cmd]
