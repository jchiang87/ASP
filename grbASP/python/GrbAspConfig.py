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
            'AGTIMESCALE', 'AGRADIUS', 'OPTIMIZER', 'NOMINAL_WINDOW']

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
        sql = 'select %s from GRB_ASP_CONFIG' % (",".join(_columns))
        def cursorFunc(cursor):
            entries = []
            for items in cursor:
                entries.append(GrbAspConfigEntry(items))
            return entries
        self.entries = apply(sql, cursorFunc)
    def find(self, met_arg):
        met = int(met_arg)
        for entry in self.entries:
            if entry.STARTDATE <= met and entry.ENDDATE >= met:
                return entry
        raise RuntimeError, "GRB ASP config not found for MET %i" % met

grbAspConfig = GrbAspConfig()

def irf_config(tstart):
    """Use the configuration from the SOURCEMONITORINGCONFIG table
    for determining the event classes and irfs.
    """
    sql = ("select irfs, ft1_filter from SOURCEMONITORINGCONFIG "
           + "where startdate<=%i and enddate>=%i" % (tstart, tstart))
    return apply(sql, lambda curs : [x for x in curs][0])

if __name__ == '__main__':
    print grbAspConfig.find(252372500)
