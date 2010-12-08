class Machine:
    def __init__(self, datastore):
        self.datastore = datastore
    def disassemble(self, id):
        """Disassemble a single instruction, returning a MachineInstruction instance."""
        pass

class MachineInstruction:
    def get_id(self):
        """Return an unique identifier associated with this machine instruction, and it's various representations."""
        pass
    def get_ir(self):
        """Return the Intermediate Representation object for this machine instruction."""
        pass
    def render(self):
        """Return a list of Render Tokens representing this machine instruction."""
        pass

class MachineBlock:
    def get_id(self):
        """Return an unique identifier associated with this machine basic-block, and it's various representations."""
        pass
    def get_ir(self):
        """Return the Intermediate Representation object for this machine basic-block."""
        # TODO: implement a default instruction-IR merge strategy.
        pass
    def render(self):
        """Return a list of Render Tokens representing this machine basic-block."""
        # TODO: implement a default instruction aggregation strategy.
        pass

class MachineFunction:
    def get_id(self):
        """Return an unique identifier associated with this machine function, and it's various representations."""
        pass
    def get_ir(self):
        """Return the Intermediate Representation object for this machine function."""
        # TODO: implement a default instruction-IR merge strategy.
        pass
    def render(self):
        """Return a list of Render Tokens representing this machine function."""
        # TODO: implement a default instruction aggregation strategy.
        pass
