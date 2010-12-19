import shared_opcode_types
import shared_mem_types
import os.path
import os

from i8051 import i8051Machine

#
# Writing your own machine plugin
#
# An machine is currently a type that provides 2 properties:
#   name: a globally unique typename used to identify this datatype
#   decode: a function that returns either None, or a dict of the disassembly results [see below]

# Disassembler return structure:
#   {
#       addr: address of the instruction in ram [what it was called with]
#       dests: list of potential new PC destinations, can be empty
#       disasm: AssemblyEncoding type - see below
#       length: number of bytes the instruction uses
#   }
#

# AssemblyEncoding: Class that pairs opcode and Operands
#
#
#    mov        a,        @dptr
#    ^opcode    ^operand  ^operand
#
#   opcode  = string of the opcode
#   operand = instance of a class that provides .render(ds) [see below]

# Operands:
#
#   Operands are classes that implement a .render method, usually derived from Operand
#   .render is called with the database as the parameter, so they can lookup symbolic names / constants / etc
#   for future compatibility, add a params=None argument to .render
#   .render returns a tuple containing a string and a operand type constant - the operand type constant is currently
#   solely used to color opcodes appropriately
#
#   Operands should be in the order of the instruction set as documented by the IC manufacturer - there is no inherent
#   dst, src order required



# HACK - load machines at startup
def loadMachineModules():
    machine_list = {}

    # Iterate across all machine directories
    my_path = os.path.dirname(__file__)
    ignores = ["common"]
    this_dir = [i for i in os.listdir(my_path) if os.path.isdir(my_path +"/"+ i) and i not in ignores]
    
    for arch_modname in this_dir:
        try:
            toplevel = __import__(__name__ + "." + arch_modname)
            module = getattr(toplevel,arch_modname)
            try:
                
                machine_list.update([ (machine.shortname, machine) for machine in module.machines ] )
            except AttributeError:
                print "Error - could not find machine list for machine %s" % arch_modname
                raise
        except:
            print "Error, could not import machine %s, skipping" % arch_modname

    return machine_list

machine_list = None

def machineFactory(datastore, archname):
    global machine_list
    if not machine_list:
        machine_list = loadMachineModules()
    return machine_list[archname](datastore)

def machineNames():
    global machine_list
    if not machine_list:
        machine_list = loadMachineModules()
    return machine_list.keys()


def getDecoder(datastore, archname):
    return machineFactory(datastore, archname)
