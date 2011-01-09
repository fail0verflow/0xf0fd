class BaseCommand(object):
    def __init__(self):
        self.__ran = False
    def execute(self):
        assert not self.__ran
        self.__ran = True

    def undo(self):
        assert self.__ran
        self.__ran = False


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
