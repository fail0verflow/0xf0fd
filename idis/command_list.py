class CommandList(object):
    def __init__(self, datastore):
        self.datastore = datastore
        self.cmds = []
        self.forward = []

    def push(self, cmd):
        self.cmds.append(cmd)
        cmd.execute(self.datastore)
        
    def rewind(self, n):
        for i in xrange(n):
            c = self.cmds.pop()
            c.undo(self.datastore)
            self.forward.append(c)

