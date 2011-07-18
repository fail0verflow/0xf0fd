from collections import defaultdict


class Xref(object):
    def __init__(self, ident_from, ident_to, xref_type):
        self.ident_from = ident_from
        self.ident_to = ident_to
        self.xref_type = xref_type


class XrefList(object):
    XREF_CODE = 1  # Dest should be treated as code
    XREF_DATA = 2  # Dest should be treated as data
    XREF_CODE_CALL = 4  # Only applicable for code xrefs
                        # should be considered a function call

    def __init__(self, parent):
        self.__parent = parent

        self.conn = parent.conn
        self.__c = self.conn.cursor()

        self.__createTables()

    def __createTables(self):
        self.__c.execute(
        '''CREATE TABLE IF NOT EXISTS xref_info (
             ident_from INTEGER,
             ident_to   INTEGER,
             type       INTEGER,
             PRIMARY KEY(ident_from, ident_to) )''')

        self.__c.execute(
        '''CREATE INDEX IF NOT EXISTS xref_from_idx
                ON xref_info (ident_from)'''
                )

        self.__c.execute(
        '''CREATE INDEX IF NOT EXISTS xref_to_idx
                ON xref_info (ident_to)'''
                )

    def clearXrefs(self):
        self.__c.execute("DELETE FROM xref_info")
        self.conn.commit()

    def delXrefFrom(self, ident_from):
        self.__c.execute(
                '''DELETE FROM xref_info
                   WHERE ident_from = ?''', (ident_from,))
        self.conn.commit()

    def addXref(self, ident_from, ident_to, xref_type):
        self.__c.execute(
                '''INSERT INTO xref_info
                      (ident_from, ident_to, type)
                   VALUES (?,?,?)''',
                (ident_from, ident_to, xref_type))

        self.conn.commit()

    def getXrefsFrom(self, ident):
        xrs = self.__c.execute(
            '''SELECT ident_from, ident_to, type
               FROM xref_info
               WHERE ident_from = ?''', (ident, )).fetchall()

        return map(lambda (x, y, z): Xref(x, y, z), xrs)

    def getXrefsTo(self, ident):
        xrs = self.__c.execute(
            '''SELECT ident_from, ident_to, type
               FROM xref_info
               WHERE ident_to = ?''', (ident, )).fetchall()

        return map(lambda (x, y, z): Xref(x, y, z), xrs)
