from idis.dbtypes import CommentPosition


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
