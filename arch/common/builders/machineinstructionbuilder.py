from arch.common.machine import MachineInstruction
def get_MachineInstructionBuilder(module,cache={}):
    class MachineInstructionBuilder(type):
        def __new__(cls,name,operands,ir_template):
            if name in cache:
                return cache[name]
            res = type.__new__(cls,name,(MachineInstruction,),{'operands':operands,'ir_template':ir_template})
            res.__module__ = module           
            cache[name] = res
            return res
        def __init__(cls,name,operands,ir_template):
            super(MachineInstructionBuilder,cls).__init__(name,operands,ir_template)
    MachineInstructionBuilder.__name__ = module.replace('.','_') + '_MIB'
    return MachineInstructionBuilder


