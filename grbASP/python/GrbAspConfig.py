"""
@brief Class to read ASP configuration for a given MET.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

from databaseAccess import *

_columns = ['ID', 'STARTDATE', 'ENDDATE', 'IRFS', 'PARTITIONSIZE',
            'THRESHOLD', 'DEADTIME', 'TIMEWINDOW', 'RADIUS', 
            'AGTIMESCALE', 'AGRADIUS', 'OPTIMIZER']

class GrbAspConfigEntry(object):
    def __init__(self, items):
        for key, value in zip(_columns, items):
            try:
                self.__dict__[key] = int(value)
            except ValueError:
                self.__dict__[key] = value
    def __repr__(self):
        return `self.__dict__`

class GrbAspConfig(object):
    def __init__(self):
        sql = 'select * from GRB_ASP_CONFIG'
        def cursorFunc(cursor):
            entries = []
            for items in cursor:
                entries.append(GrbAspConfigEntry(items))
            return entries
        self.entries = apply(sql, cursorFunc)
    def find(self, met):
        for entry in self.entries:
            if entry.STARTDATE <= met and entry.ENDDATE >= met:
                return entry
        raise RuntimeError, "GRB ASP config not found for MET %i" % met

grbAspConfig = GrbAspConfig()

if __name__ == '__main__':
    print grbAspConfig.find(252372500)
