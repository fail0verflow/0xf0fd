from arch.common.machine import MachineInstruction
def get_MachineInstructionBuilder(module,base=MachineInstruction,cache={}):
    class MachineInstructionBuilder(type):
        def __new__(cls,name,ir_template):
            if name in cache:
                return cache[name]
            res = type.__new__(cls,name,(base,),{'mnemonic':name,'ir_template':ir_template})
            res.__module__ = module           
            cache[name] = res
            return res
        def __init__(cls,name,ir_template):
            super(MachineInstructionBuilder,cls).__init__(name)
    MachineInstructionBuilder.__name__ = module.replace('.','_') + '_MIB'
    return MachineInstructionBuilder


