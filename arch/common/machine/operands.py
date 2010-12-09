class MachineOperand(object):
    def __init__(self,name):
        self.name = name
        self.value = None
    def render(self):
        """Return a Render Token for this operand."""
        pass

class MachineRegisterOperand(MachineOperand):
    def __init__(self,name,regno):
        super(MachineRegisterOperand,self).__init__(name)
        self.value = regno

class MachineImmediateOperand(MachineOperand):
    def __init__(self,name,value,width=None):
        super(MachineImmediateOperand,self).__init__(name)
        self.value = value
        self.width = width
