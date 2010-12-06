

import idis.tools
import idis.tools_algos
import arch

from inspect import InspectWindow

from PySide import QtCore
from PySide import QtGui

keyList = dict([(getattr(QtCore.Qt, key), key) for key in dir(QtCore.Qt) if key.startswith('Key')])

class CommandHandler(object):
	def handleInspect(self, addr):
		info = self.ds[addr]
		iw = InspectWindow(info)
		iw.show()
		self.iws += [iw]
		
	def handleSetLabel(self, addr):
		oldlabel = self.ds[addr].label
		text, ok = QtGui.QInputDialog.getText(None, "Set Label", "Enter a label for addr %04x" % addr, text=oldlabel)
		if ok:
			self.ds[addr].label = text


		
	def handleCodeFollow(self, addr):
		# TODO Hack
		a = arch.architectureFactory('8051')
		idis.tools_algos.codeFollow(self.ds, a, addr)

	def handleFollowJump(self, addr):
		newaddr = idis.tools.follow(self.ds, addr)
		try:
			self.ds[newaddr]
			self.memstack = [(self.view.getTopAddr(), self.view.getSelAddr())]
				
			self.view.setTopAddr(newaddr)
			self.view.setSelAddr(newaddr)
				
		except KeyError:
			pass


	def handleCodeReturn(self, addr):
		try:
			top,sel = self.memstack.pop()
		except AttributeError:
			return
		
		self.view.setTopAddr(top)
		self.view.setSelAddr(sel)
		
	def __init__(self, ds, view):
		self.iws = []
		self.ds = ds
		self.memstack = []
		self.view = view
		self.cmd_handlers = {
			QtCore.Qt.Key_I: self.handleInspect,
			QtCore.Qt.Key_C: self.handleCodeFollow,
			QtCore.Qt.Key_Return: self.handleFollowJump,
			QtCore.Qt.Key_L: self.handleSetLabel,
			QtCore.Qt.Key_Backspace: self.handleCodeReturn
			}
		
	def handleCommand(self, addr, cmd):
		try:
			self.cmd_handlers[cmd](addr)
		except KeyError:
			print keyList[cmd]