class MachineOperand(object):
    def __init__(self,name):
        self.name = name
        self.value = None
    
    # FIXME: implement real rendering system
    def render(self, context):
        """Return a Render Token for this operand."""
        return self.name, 0

class MachineRegisterOperand(MachineOperand):
    def __init__(self,name,regno):
        super(MachineRegisterOperand,self).__init__(name)
        self.value = regno

class MachineImmediateOperand(MachineOperand):
    def __init__(self,name,value,width=None):
        super(MachineImmediateOperand,self).__init__(name)
        self.value = value
        self.width = width

class MachineMemoryOperand(MachineOperand):
    def __init__(self,name,base,offset):
        super(MachineMemoryOperand,self).__init__(name)
        self.base = base
        self.offset = offset
