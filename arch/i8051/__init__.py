import opcode_8051

class i8051Machine(object):
    shortname = "8051"
    longname = "8051"

    def __init__(self, datastore):
        self.datastore = datastore
        
    def disassemble(self, id, saved_params):
        bytes = self.datastore.readBytes(id, 5)
        return opcode_8051.decode_bytes(id, bytes)


machines = [i8051Machine]   


