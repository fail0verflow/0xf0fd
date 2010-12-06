import opcode_8051

class Arch8051(object):
	name = '8051'
	maxInsnLength = 3
	decode = staticmethod(opcode_8051.decode)

	