from arch.common import bits
class MachineCodec(object):
    def decode(self,data):
        """Decode the passed data, returning a MachineInstruction."""
        pass
    def encode(self,instruction):
        """Encode the passed instruction, returning a binary representation."""
        pass
       
class TableCodec(MachineCodec):
    def __init__(self,col_bitrange, row_bitrange, decode_table):
        self.col_bitrange = col_bitrange
        self.row_bitrange = row_bitrange
        self.decode_table = decode_table
        
        self.encode_table = {}
        for row in range(len(self.decode_table)):
            for col in range(len(self.decode_table[row])):
                self.encode_table[self.decode_table[row][col]] = (col,row)

    def decode(self, data):
        decoder_name = self.decode_table[bits.get(data,*self.row_bitrange)][bits.get(data,*self.col_bitrange)]
        return decoder_name and getattr(self,decoder_name)(data)

    def encode(self,instruction):
        #TODO: implement the encoder.
        pass
