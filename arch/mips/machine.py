from arch.common.machine import *
import arch.common.bits as bits
from arch.common.builders import get_MachineInstructionBuilder
MIB = get_MachineInstructionBuilder('arch.mips.machine')

MRO = MachineRegisterOperand
MIO = MachineImmediateOperand

class MIPSCodec(TableCodec):
    class SpecialCodec(TableCodec):
        def __init__(self):
            table = [ # bits 5..3 down, 2..0 across
                    ['_d_sll',   '_d_movci',  '_d_srl',    '_d_sra',    '_d_sllv',   None,   '_d_srlv',   '_d_srav'],
                    ['_d_jr',    '_d_jalr',   '_d_movz',   '_d_movn',   '_d_syscall','_d_break',  None,   '_d_sync'],
                    ['_d_mfhi',  '_d_mthi',   '_d_mflo',   '_d_mtlo',   None,   None,   None,   None],
                    ['_d_mult',  '_d_multu',  '_d_div',    '_d_divu',   None,   None,   None,   None],
                    ['_d_add',   '_d_addu',   '_d_sub',    '_d_subu',   '_d_and',    '_d_or',     '_d_xor',    '_d_nor'],
                    [None,  None,   '_d_slt',    '_d_sltu',   None,   None,   None,   None],
                    ['_d_tge',   '_d_tgeu',   '_d_tlt',    '_d_tltu',   '_d_teq',    None,   '_d_tne',    None],
                    [None,  None,   None,   None,   None,   None,   None,   None]
                    ]
            TableCodec.__init__(self,(2,0),(5,3),table)
                    
        def _d_sll(self,data):
            return None   
        def _d_movci(self,data):
            return None  
        def _d_srl(self,data):
            return None    
        def _d_sra(self,data):
            return None    
        def _d_sllv(self,data):
            return None      
        def _d_srlv(self,data):
            return None   
        def _d_srav(self,data):
            return None
                    
        def _d_jr(self,data):
            return None    
        def _d_jalr(self,data):
            return MIB('jalr',(MRO('target',bits.get(data,25,21)), MRO('return',bits.get(data,15,11))),None)

        def _d_movz(self,data):
            return None   
        def _d_movn(self,data):
            return None   
        def _d_syscall(self,data):
            return None
        def _d_break(self,data):
            return None     
        def _d_sync(self,data):
            return None
                    
        def _d_mfhi(self,data):
            return None  
        def _d_mthi(self,data):
            return None   
        def _d_mflo(self,data):
            return None   
        def _d_mtlo(self,data):
            return None            
                    
        def _d_mult(self,data):
            return None  
        def _d_multu(self,data):
            return None  
        def _d_div(self,data):
            return None    
        def _d_divu(self,data):
            return None            
                    
        def _d_add(self,data):
            return None   
        def _d_addu(self,data):
            return None   
        def _d_sub(self,data):
            return None    
        def _d_subu(self,data):
            return None   
        def _d_and(self,data):
            return None    
        def _d_or(self,data):
            return None     
        def _d_xor(self,data):
            return None    
        def _d_nor(self,data):
            return None
                         
        def _d_slt(self,data):
            return None    
        def _d_sltu(self,data):
            return None            
                    
        def _d_tge(self,data):
            return None   
        def _d_tgeu(self,data):
            return None   
        def _d_tlt(self,data):
            return None    
        def _d_tltu(self,data):
            return None   
        def _d_teq(self,data):
            return None       
        def _d_tne(self,data):
            return None    

    class RegimmCodec(TableCodec):
        def __init__(self):
            table = [ # bits 20..19 down, 18..16 across
                    ['bltz',      'bgez',   'bltzl',      'bgezl',      None,   None,   None,   None],
                    ['tgei',      'tgeiu',  'tlti',       'tltiu',      'teqi',   None,   'tnei',   None],
                    ['bltzal',    'bgezal', 'btlzall',    'bgezall',    None,   None,   None,   None],
                    [None,      None,   None,       None,       None,   None,   None,   'synci']
                    ]
            TableCodec.__init__(self, (18,16), (20,19), table)
                    
        def _d_bltz(self,data):
            return None      
        def _d_bgez(self,data):
            return None   
        def _d_bltzl(self,data):
            return None      
        def _d_bgezl(self,data):
            return None               
        def _d_tgei(self,data):
            return None      
        def _d_tgeiu(self,data):
            return None  
        def _d_tlti(self,data):
            return None       
        def _d_tltiu(self,data):
            return None      
        def _d_teqi(self,data):
            return None      
        def _d_tnei(self,data):
            return None   
        def _d_bltzal(self,data):
            return None    
        def _d_bgezal(self,data):
            return None 
        def _d_btlzall(self,data):
            return None    
        def _d_bgezall(self,data):
            return None             
        def _d_synci(self,data):
            return None
    class Special2Codec(TableCodec):
        def __init__(self):
            table = [ # bits 5..3 down, 2..0 across
                    ['madd',  'maddu',  'mul',    None,   'msub',   'msubu',  None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   None],
                    ['clz',   'clo',    None,   None,   None,   None,   None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   None],
                    [None,  None,   None,   None,   None,   None,   None,   'sdbbp']
                    ]
            TableCodec.__init__(self, (2,0), (5,3), table)
                    
        def _d_madd(self,data):
            return None  
        def _d_maddu(self,data):
            return None  
        def _d_mul(self,data):
            return None       
        def _d_msub(self,data):
            return None   
        def _d_msubu(self,data):
            return None     
        def _d_clz(self,data):
            return None   
        def _d_clo(self,data):
            return None                   
        def _d_sdbbp(self,data):
            return None
    class Special3Codec(TableCodec):
        def __init__(self):
            table = [ # bits 5..3 down, 2..0 across
                ['ext',   None,   None,   None,   'ins',    None,   None,   None],
                [None,  None,   None,   None,   None,   None,   None,   None],
                [None,  None,   None,   None,   None,   None,   None,   None],
                [None,  None,   None,   None,   None,   None,   None,   None],
                ['bshfl', None,   None,   None,   None,   None,   None,   None],
                [None,  None,   None,   None,   None,   None,   None,   None],
                [None,  None,   None,   None,   None,   None,   None,   None],
                [None,  None,   None,   'rdhwr',  None,   None,   None,   None]
                ]
            TableCodec.__init__(self, (2,0), (5,3), table)
        def _d_ext(self,data):
            return None
        def _d_ins(self,data):
            return None
        def _d_bshfl(self,data):
            return None
        def _d_rdhwr(self,data):
            return None
    def __init__(self):
        table = [ #bits 31..29 down; 28..26 across
                ['_d_special', '_d_regimm',   '_d_j',    '_d_jal',  '_d_beq',      '_d_bne',  '_d_blez', '_d_bgtz'],
                ['_d_addi',    '_d_addiu',    '_d_slti', '_d_sltiu','_d_andi',     '_d_ori',  '_d_xori', '_d_lui'],
                ['_d_cop0',    '_d_cop1',     '_d_cop2', '_d_cop1x','_d_beql',     '_d_bnel', '_d_blezl','_d_bgtzl'],
                [None,      None,       None,   None,   '_d_special2', '_d_jalx', None,   '_d_special3'],
                ['_d_lb',      '_d_lh',       '_d_lwl',  '_d_lw',   '_d_lbu',      '_d_lhu',  '_d_lwr',  None],
                ['_d_sb',      '_d_sh',       '_d_swl',  '_d_sw',   None,       None,   '_d_swr',  '_d_cache'],
                ['_d_ll',      '_d_lwc1',     '_d_lwc2', '_d_pref', None,       '_d_ldc1', '_d_ldc2', None],
                ['_d_sc',      '_d_swc1',     '_d_swc2', None,   None,       '_d_sdc1', '_d_sdc2', None]
                ]
        TableCodec.__init__(self,(28,26),(31,29),table)
        self.class_decoders = { 
                'special' :MIPSCodec.SpecialCodec(),
                'regimm'  :MIPSCodec.RegimmCodec(),
                'special2':MIPSCodec.Special2Codec(),
                'special3':MIPSCodec.Special3Codec()
                }

    def _d_special(self,data):
        return self.class_decoders['special'].decode(data)
    def _d_regimm(self,data):
        return self.class_decoders['regimm'].decode(data)
    def _d_j(self,data):
        return None
    def _d_jal(self,data):
        return None
    def _d_beq(self,data):
        return None
    def _d_bne(self,data):
        return None
    def _d_blez(self,data):
        return None
    def _d_bgtz(self,data):
        return None
    def _d_addi(self,data):
        return None
    def _d_addiu(self,data):
        return None
    def _d_slti(self,data):
        return None
    def _d_sltiu(self,data):
        return None
    def _d_andi(self,data):
        return None
    def _d_ori(self,data):
        return None
    def _d_xori(self,data):
        return None
    def _d_lui(self,data):
        return None
    def _d_cop0(self,data):
        return None
    def _d_cop1(self,data):
        return None
    def _d_cop2(self,data):
        return None
    def _d_cop1x(self,data):
        return None
    def _d_beql(self,data):
        return None
    def _d_bnel(self,data):
        return None
    def _d_blezl(self,data):
        return None
    def _d_bgtzl(self,data):
        return None
    def _d_special2(self,data):
        return self.class_decoders['special2'].decode(data)
    def _d_jalx(self,data):
        return None
    def _d_special3(self,data):
        return self.class_decoders['special3'].decode(data)
    def _d_lb(self,data):
        return None
    def _d_lh(self,data):
        return None
    def _d_lwl(self,data):
        return None
    def _d_lw(self,data):
        return None
    def _d_lbu(self,data):
        return None
    def _d_lhu(self,data):
        return None
    def _d_lwr(self,data):
        return None
    def _d_sb(self,data):
        return None
    def _d_sh(self,data):
        return None
    def _d_swl(self,data):
        return None
    def _d_sw(self,data):
        return None
    def _d_swr(self,data):
        return None
    def _d_cache(self,data):
        return None
    def _d_ll(self,data):
        return None
    def _d_lwc1(self,data):
        return None
    def _d_lwc2(self,data):
        return None
    def _d_pref(self,data):
        return None
    def _d_ldc1(self,data):
        return None
    def _d_ldc2(self,data):
        return None
    def _d_sc(self,data):
        return None
    def _d_swc1(self,data):
        return None
    def _d_swc2(self,data):
        return None
    def _d_sdc1(self,data):
        return None
    def _d_sdc2(self,data):
        return None


class MIPSMachine(Machine):
    def __init__(self,datastore):
        self.datastore = datastore
        self.codec = MIPSCodec()

    def disassemble(self, id):
        data = self.datastore.readBytes(id,4)
        return self.codec.decode(data)
