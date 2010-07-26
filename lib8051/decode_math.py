from decutils import *


def decode_inc_iram(pc, opc, addr):
	return DictProxy(
				addr = pc,
				disasm = AE("inc", a_D(addr)),
				dests = [pc + 2],
				cycles = 2,
				length = 2
			)


def decode_dec_iram(pc, opc, addr):
	return DictProxy(
				addr = pc,
				disasm = AE("dec", a_D(addr)),
				dests = [pc + 2],
				cycles = 2,
				length = 2
			)


def decode_inc_dptr(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = AE("inc", a_DPTR()),
				dests = [pc + 1],
				cycles = 2,
				length = 1
			)
			
def decode_inc_reg(pc, opc):
	return DictProxy(
				addr = pc,
				disasm = AE("inc", a_R(opc&0x7)),
				dests = [pc + 1],
				cycles = 1,
				length = 1
			)

def decode_add_a_iram(pc, opc, iram_addr, carry=False):
	carry_c = "c" if carry else ""
	return DictProxy(
			addr = pc,
			disasm = AE("add%s" % carry_c, a_A(), a_D(iram_addr)),
			dests = [pc + 2],
			cycles = 1,
			length = 2
			)
						
def decode_add_a_reg(pc, opc, carry=False):
	carry_c = "c" if carry else ""
	return DictProxy(
			addr = pc,
			disasm = AE("add%s" % carry_c, a_A(), a_R(opc & 0x7)),
			dests = [pc + 1],
			cycles = 1,
			length = 1
			)		
				
def decode_add_a_imm(pc, opc, immediate, carry=False):
	carry_c = "c" if carry else ""
	return DictProxy(
			addr = pc,
			disasm = AE("add%s" % carry_c, a_A(), a_I8(immediate)),
			dests = [pc + 2],
			cycles = 1,
			length = 2
			)

def decode_add_a_ind(pc, opc, carry=False):
	carry_c = "c" if carry else ""
	return DictProxy(
			addr = pc,
			disasm = AE("add%s" % carry_c, a_A(), a_RI(opc&0x1)),
			dests = [pc + 1],
			cycles = 1,
			length = 1
			)


def decode_cpl_a(pc, opc):
	return DictProxy(
			addr = pc,
			disasm = AE("cpl", a_A()),
			dests = [pc + 1],
			cycles = 1,
			length = 1
			)
