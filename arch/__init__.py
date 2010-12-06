import shared_opcode_types
import shared_mem_types
from lib8051 import Arch8051

#
# Writing your own architecture plugin
#
# An architecture is currently a type that provides 2 properties:
#	name: a globally unique typename used to identify this datatype
#	decode: a function that returns either None, or a dict of the disassembly results [see below]

# Disassembler return structure:
#	{
#		addr: address of the instruction in ram [what it was called with]
#		dests: list of potential new PC destinations, can be empty
#		disasm: AssemblyEncoding type - see below
#		length: number of bytes the instruction uses
#	}
#

# AssemblyEncoding: Class that pairs opcode and Operands
#
#
#    mov        a,        @dptr
#    ^opcode    ^operand  ^operand
#
#	opcode  = string of the opcode
#	operand = instance of a class that provides .render(ds) [see below]

# Operands:
#
#	Operands are classes that implement a .render method, usually derived from Operand
#	.render is called with the database as the parameter, so they can lookup symbolic names / constants / etc
#	for future compatibility, add a params=None argument to .render
#	.render returns a tuple containing a string and a operand type constant - the operand type constant is currently
#	solely used to color opcodes appropriately
#
#	Operands should be in the order of the instruction set as documented by the IC manufacturer - there is no inherent
#	dst, src order required




# TODO: Rewrite this file: this should properly search all architectures and plugins
architecture_list = {
	Arch8051.name: Arch8051
}

def architectureFactory(archname):
	return architecture_list[archname]()

def architectureNames():
	return architecture_list.names()

def getDecoder(dec_type):
	try:
		return shared_mem_types.decoderTypes[dec_type]
	except KeyError:
		return architectureFactory(dec_type).decode