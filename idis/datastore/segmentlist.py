from cPickle import *
import zlib
import sqlite3

class Segment(object):
    def __init__(self, data, base_addr, name=""):
        self.__data = data
        self.__base_addr = base_addr
        self.__name = name

    def __getlength(self):
        return len(self.__data)
    length = property(__getlength)
    
    def __getbaseaddr(self):
        return self.__base_addr
    base_addr = property(__getbaseaddr)
    
    def readBytes(self, start, length = 1):
        if (start < self.__base_addr or start >= self.__base_addr + self.__getlength()):
            raise IOError, "not in segment"
        return self.__data[start-self.__base_addr:start-self.__base_addr+length]



class SegmentList(object):
    def __init__(self, conn, ds):
        self.__conn = conn
        
        self.segments_cache = []
        self.__populateSegments()
        self.ds = ds

    def __iter__(self):
        return self.segments_cache.__iter__()

    def __populateSegments(self):
        for i in self.__conn.execute('''SELECT obj  FROM segments'''):
            self.segments_cache.append(loads(zlib.decompress(i[0])))

    def addSegment(self, segment):
        self.segments_cache.append(segment)
        dbstr = sqlite3.Binary(zlib.compress(dumps(segment)))
        self.__conn.execute('''INSERT INTO segments (base_addr, obj) VALUES (?,?)''',
              (segment.base_addr,dbstr))

        self.ds.layoutChanged()
