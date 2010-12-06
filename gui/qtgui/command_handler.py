

import idis.tools
import idis.tools_algos
import arch

from PySide import QtCore
from PySide import QtGui

keyList = dict([(getattr(QtCore.Qt, key), key) for key in dir(QtCore.Qt) if key.startswith('Key')])

def handleSetLabel(ds, win, view, addr):
	oldlabel = ds[addr].label
	text, ok = QtGui.QInputDialog.getText(win, "Set Label", "Enter a label for addr %04x" % addr, text=oldlabel)
	if ok:
		ds[addr].label = text


	
def handleCodeFollow(ds, win, view, addr):
	# TODO Hack
	a = arch.architectureFactory('8051')
	idis.tools_algos.codeFollow(ds, a, addr)

def handleFollowJump(ds, win, view, addr):
	newaddr = idis.tools.follow(ds, addr)
	try:
		ds[newaddr]
		try:
			win.memstack += [(view.getTopAddr(), view.getSelAddr())]
		except AttributeError:
			win.memstack = [(view.getTopAddr(), view.getSelAddr())]
			
		view.setTopAddr(newaddr)
		view.setSelAddr(newaddr)
			
	except KeyError:
		pass


def handleCodeReturn(ds, win, view, addr):
	try:
		top,sel = win.memstack.pop()
	except AttributeError:
		return
	
	view.setTopAddr(top)
	view.setSelAddr(sel)
	
cmd_handlers = {
	QtCore.Qt.Key_C: handleCodeFollow,
	QtCore.Qt.Key_Return: handleFollowJump,
	QtCore.Qt.Key_L: handleSetLabel,
	QtCore.Qt.Key_Backspace: handleCodeReturn
	}
	
def handleCommand(ds, win, view, addr, cmd):
	try:
		cmd_handlers[cmd](ds, win, view, addr)
	except KeyError:
		print keyList[cmd]