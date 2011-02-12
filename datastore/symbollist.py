from fsignal_thunk import *


class Symbol(object):
    TYPE_LOCAL = 0
    TYPE_FNENT = 1
    TYPE_MULTIUSE = 2

    def __init__(self, datastore, address, name, type=TYPE_LOCAL):
            self.ds = datastore
            self.address = address
            self.name = name
            self.type = type

    def __str__(self):
        return self.name


class SymbolList(object):
    """ SymbolList provides a view onto the list of symbols in the database"""
    def __init__(self, connection, table):
        self.conn = connection
        self.symbolsChanged = FSignal()

    def __len__(self):
        return self.conn.execute(
            '''SELECT COUNT(*) FROM symbols''' % table).fetchall()[0]

    def getSymbol(self, addr):
        """getSymbol returns the textual symbol
            name associated with an address"""
        try:
            return str(self.conn.execute(
                '''SELECT name FROM symbols WHERE addr = ?''',
                (addr,)).fetchall()[0][0])

        except IndexError:
            return None

    def setSymbol(self, addr, text):
        """setSymbol sets a text symbol at a specified address"""
        self.conn.execute('''DELETE FROM symbols WHERE addr=?''',
              (addr,))

        if text:
            self.conn.execute(
                '''INSERT INTO symbols (addr, name) VALUES (?,?)''',
                (addr, text))

        self.symbolsChanged.emit()

    def listInterface(self, order, order_dir, index):
        """ listInterface provides an ordered view onto the symbol list.
            order is specified by order, with values of "addr" or "name"
            and by order_dir with values of "ASC" or "DESC"
        """
        assert order in ["addr", "name"]
        assert order_dir in ["ASC", "DESC"]

        return self.conn.execute('''SELECT addr, name
                                    FROM symbols
                                    ORDER BY %s %s
                                    LIMIT ?, 1''' %
                                    (order, order_dir), (index,)).fetchone()

    def __len__(self):
        return self.conn.execute(
            '''SELECT COUNT(*) FROM symbols''').fetchall()[0][0]
