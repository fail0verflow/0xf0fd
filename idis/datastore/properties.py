from cPickle import dumps, loads

class Properties(object):
    def __init__(self, connection):
        self.conn = connection

    def get(self, key, default = None):
        row = self.conn.execute('''SELECT value FROM properties WHERE prop_key = ? ''', (key,)).fetchone()

        if row:
            return loads(str(row[0]))

        if default != None:
            return default

        raise KeyError

    def set(self, key, value):
        self.conn.execute('''DELETE FROM properties WHERE prop_key = ?''', (key, ))

        if value != None:
            self.conn.execute('''INSERT INTO properties (prop_key, value) VALUES (?,?)''', (key, dumps(value)))


