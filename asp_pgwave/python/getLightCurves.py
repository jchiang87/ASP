import numarray as num
from databaseAccess import *

def getSourceList():
    sql = "select * from SOURCEMONITORINGDATA"
    def cursorFunc(cursor):
        entries = {}
        for item in cursor:
            entries[item[0]] = 1
        sources = entries.keys()
        sources.sort()
        return sources
    return apply(sql, cursorFunc)

def getLightCurve(source):
    sql = "select * from SOURCEMONITORINGDATA where SOURCENAME = '%s'" % source
    def cursorFunc(cursor):
        tmin, tmax, value, error = [], [], [], []
        for item in cursor:
            tmin.append(item[2])
            tmax.append(item[3])
            value.append(item[4])
            error.append(item[5])
        return [num.array(x) for x in (tmin, tmax, value, error)]
    return apply(sql, cursorFunc)

if __name__ == '__main__':
    sources = getSourceList()
