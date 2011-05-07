from datastore.dbtypes import CommentPosition
from datastore.infostore import InfoStore


class BaseCommand(object):
    def __init__(self):
        self.__ran = False

    def execute(self):
        assert not self.__ran
        self.__ran = True

    def undo(self):
        assert self.__ran
        self.__ran = False

    def _markAlreadyRan(self):
        """ WARNING - call this function with care -
        about the only valid use is when adding a SuperCommand to the command
        stack where the commands have been executed individually"""
        self.__ran = True


class SetTypeCommand(BaseCommand):
    # dtype_name = None means undefine
    # type_len is the length of the data that will be constructed
    #   only use if the length is known beforehand - just an optimization
    def __init__(self, ident, dtype_name, type_len=None):
        BaseCommand.__init__(self)
        self.__ident = ident
        self.__dtn = dtype_name
        self.__type_len = type_len

        # HACK: This should be optional, need to fix typesystem first
        assert not dtype_name or type_len != None

        # Ensure we don't have a long remove
        assert dtype_name or type_len == None

    def doLU(self, datastore, i):
        rcode, lu = datastore.infostore.lookup(i)
        if rcode != InfoStore.LKUP_OK:
            return None
        return lu.typename

    def execute(self, datastore):
        BaseCommand.execute(self)

        # Backup existing typenames
        self.__bk = [self.doLU(datastore, i) for i in xrange(self.__ident,
            self.__ident + self.__type_len)]

        # either do re
        if self.__dtn:
            datastore.infostore.setType(self.__ident, self.__dtn)
        else:
            datastore.infostore.remove(self.__ident)

    def undo(self, datastore):
        BaseCommand.undo(self)
        for ident_o, tn in enumerate(self.__bk):
            if not tn:
                datastore.infostore.remove(self.__ident + ident_o)
            else:
                datastore.infostore.setType(self.__ident + ident_o, tn)


class CommentCommand(BaseCommand):
    def __init__(self, ident, position, text):
        BaseCommand.__init__(self)
        assert position != None
        assert position in CommentPosition.__dict__.values()
        self.__ident = ident
        self.__newtext = text
        self.__position = position

    def execute(self, datastore):
        BaseCommand.execute(self)
        self.__undocomment = datastore.comments.getCommentText(
            self.__ident, self.__position)
        datastore.comments.setComment(
            self.__ident, self.__newtext, self.__position)

    def undo(self, datastore):
        BaseCommand.undo(self)
        datastore.comments.setComment(
            self.__ident, self.__undocomment, self.__position)


class SymbolNameCommand(BaseCommand):
    def __init__(self, ident, name):
        BaseCommand.__init__(self)
        self.__ident = ident
        self.__newname = name

    def execute(self, datastore):
        BaseCommand.execute(self)
        self.__undoname = datastore.symbols.getSymbol(self.__ident)
        datastore.symbols.setSymbol(self.__ident, self.__newname)

    def undo(self, datastore):
        BaseCommand.undo(self)
        datastore.symbols.setSymbol(self.__ident, self.__undoname)


class CompoundCommand(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)
        self.cmds = []

    def add(self, cmd):
        self.cmds.append(cmd)

    def execute(self, datastore):
        BaseCommand.execute(self)

        for i in self.cmds:
            i.execute(datastore)

    def getInternalList(self):
        return cmds

    def undo(self, datastore):
        BaseCommand.undo(self)
        for i in self.cmds[::-1]:
            i.undo(datastore)
