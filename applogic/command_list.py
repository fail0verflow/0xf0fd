

class CommandList(object):
    def __init__(self, datastore):
        self.datastore = datastore
        self.cmds = []
        self.forward = []

        self.wrap_stack = []

    def __get_wrapped(self):
        return len(self.wrap_stack) > 0
    wrapped = property(__get_wrapped)

    def supercommand_wrap(self, callback):
        # Push all wrapped commands into a "CompoundCommand" so
        # they are undone as a block

        from cmd import CompoundCommand
        s = CompoundCommand()
        self.wrap_stack.append(self.cmds)
        self.cmds = s.getInternalList()
        callback()
        self.cmds = self.wrap_stack.pop()
        s._markAlreadyRan()
        self.cmds.append(s)

    def push(self, cmd):
        self.cmds.append(cmd)
        cmd.execute(self.datastore)

    def rewind(self, n):

        n_to_do = min(n, len(self.cmds))

        for i in xrange(n_to_do):
            c = self.cmds.pop()
            c.undo(self.datastore)
            self.forward.append(c)
