
class CommentList(object):
    def __init__(self, connection, table):
        self.conn = connection
        
    def __len__(self):
        return self.conn.execute('''SELECT COUNT(*) FROM comments''' % table).fetchall()[0]

    # Objects are only temporary, don't keep around
    def getComments(self, addr, position=None):
        if position == None:
            return self.conn.execute('''SELECT text, position FROM comments WHERE addr = ?''', (addr,)).fetchall()
        return self.conn.execute('''SELECT text FROM comments WHERE addr = ? AND position = ?''', (addr, position)).fetchone()
    
    def setComment(self, addr, text, position):
        self.conn.execute('''DELETE FROM comments WHERE addr=? AND position=?''',
              (addr,position))
              
        if text:
            self.conn.execute('''INSERT INTO comments (addr, text, position) VALUES (?,?,?)''',
                (addr,text,position))
                
