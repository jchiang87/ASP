"""
@file SourceData.py

@brief Encapsulation of fitted data for each source.  This provides 
methods for updating the LIGHTCURVES database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import databaseAccess as dbAccess
cx_Oracle = dbAccess.cx_Oracle

def getMonitoringBand(emin=100, emax=300000):
    sql = ("select eband_id from ENERGYBANDS where emin=%i and emax=%i "
           % (emin, emax) + "and group_id=0")
    def getBand(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, getBand)

_monitoringBand = getMonitoringBand()

class SourceTypeError(RuntimeError):
    "Requested source is not in POINTSOURCES table"

class SourceData(object):
    _upperThreshold = 2e-6
    _lowerThreshold = 2e-7
    def __init__(self, name, flux, fluxerr, srcModel, TS, isUL=False):
        self.name = name
        self.flux, self.fluxerr = flux, fluxerr
        self.type = self._getSrcType()
        self.srcModel = srcModel
        self.TS = TS
        self.isUL = isUL
        try:
            self.eband_id = int(os.environ['eband_id'])
        except KeyError:
            #print "SourceData: eband_id env var not set"
            #print ("Setting eband_id to " + "%i" % _monitoringBand + 
            #       " for 100 MeV to 300 GeV")
            self.eband_id = _monitoringBand
        self.interval_number = int(os.environ['interval'])
        self.frequency = os.environ['frequency']
        self.is_monitored = self._monitoredState()
        self.pkDict = {"PTSRC_NAME" : "'%s'" % self.name,
                       "EBAND_ID" : self.eband_id,
                       "INTERVAL_NUMBER" : self.interval_number,
                       "FREQUENCY" : "'%s'" % self.frequency}
        self.rowDict = {"FLUX" : self.flux,
                        "ERROR" : self.fluxerr,
                        "TEST_STATISTIC" : self.TS,
                        "IS_UPPER_LIMIT" : int(self.isUL),
                        "IS_MONITORED" : int(self.is_monitored),
                        "IS_FLARING" : 0,
                        "XMLFILE" : "'%s'" % self.srcModel}
    def _getSrcType(self):
        sql = ("select SOURCE_TYPE from POINTSOURCES where PTSRC_NAME='%s'" %
               self.name)
        try:
            type = dbAccess.apply(sql, lambda curs : [x[0] for x in curs][0])
            return type
        except IndexError, message:
            print sql
            message = "Requested source, %s, is not in database" % self.name
            raise SourceTypeError, message
    def _monitoredState(self):
        """On daily time scales, the monitored state of a non-DRP source
        depends only on the current flux and its state in the previous
        interval in the 100 MeV to 300 GeV band."""
        if (self.type == "DRP" 
            or (self.flux > self._upperThreshold and not self.isUL)):
            return True
        # According to the DRP, we only care about this value for
        # daily and weekly monitoring.
        if not self.frequency in ("daily", "weekly"):
            return False
        if self.frequency == "daily" and self.eband_id == _monitoringBand:
            return self._monitoredBandState()
        #
        # Default action: return True if the monitored band is True
        # at any time during the current interval.
        #
        sql = ("select INTERVAL_NUMBER from TIMEINTERVALS where " +
               "FREQUENCY = 'daily' and " +
               "TSTART >= %i and " % int(os.environ['TSTART']) +
               "TSTOP <= %i" % int(os.environ['TSTOP']))
        def getIntervals(cursor):
            intervals = [entry[0] for entry in cursor]
            # These should be continguous, so just need endpoints.
            return min(intervals), max(intervals)
        try:
            ilims = dbAccess.apply(sql, getIntervals)
        except StandardError, message:
            print sql
            raise StandardError, message
        sql = ("select IS_MONITORED from LIGHTCURVES where " +
               "PTSRC_NAME = '%s' and " % self.name + 
               "EBAND_ID = %i and " % _monitoringBand +
               "FREQUENCY = 'daily' and " +
               "INTERVAL_NUMBER <= %i and INTERVAL_NUMBER >= %i" % ilims)
        def getState(cursor):
            for entry in cursor:
                if int(entry[0]):
                    return True
            return False
        return dbAccess.apply(sql, getState)
    def _monitoredBandState(self):
        if self.flux < self._lowerThreshold or self.isUL:
            return False
        # Use the current flux value and the previous is_monitored
        # state to compute the current is_monitored state
        previous_interval = self.interval_number - 1
        sql = ("select IS_MONITORED from LIGHTCURVES WHERE " +
               "PTSRC_NAME='%s' and " % self.name +
               "EBAND_ID=%i and " % _monitoringBand + 
               "INTERVAL_NUMBER=%i and " % previous_interval +
               "FREQUENCY='daily'")
        def getState(cursor):
            for entry in cursor:
                return entry[0]
        previous_state = dbAccess.apply(sql, getState)
        #
        # This will not be necessary once the is_monitored column is an integer.
        #
        if previous_state is None:
            previous_state = 0
        else:
            previous_state = int(previous_state)
        if (previous_state and not self.isUL 
            and self.flux > self._lowerThreshold):
            return True
        else:
            return False
    def insertDbEntry(self):
        keys = (",".join(self.pkDict.keys()) + "," +
                ",".join(self.rowDict.keys()))
        values = (",".join(["%s" % x for x in self.pkDict.values()]) + "," +
                  ",".join(["%s" % x for x in self.rowDict.values()]))
        sql = "insert into LIGHTCURVES (%s) values (%s)" % (keys, values)
        print sql
        print
        try:
            dbAccess.apply(sql)
        except cx_Oracle.IntegrityError:
            # Assume this entry already exists and this is a unique
            # constraint PK violation. Update the entry instead.
            self.updateDbEntry()
    def updateDbEntry(self):
        pk_condition = ' and '.join(["%s=%s" % (x, self.pkDict[x]) 
                                     for x in self.pkDict])
        assignments = ','.join(["%s=%s" % (x, self.rowDict[x]) 
                                for x in self.rowDict])
        sql = "update LIGHTCURVES set %s where %s" % (assignments, pk_condition)
        print sql
        print
        dbAccess.apply(sql)

if __name__ == '__main__':
    os.environ['frequency'] = 'daily'
    os.environ['TSTART'] = '257644800'
    os.environ['TSTOP'] = '257731200'
    
    #src = "BM_OS319"
    src = "Mrk 501"

    os.environ['interval'] = '0'
    foo = SourceData(src, 3e-6, 1e-7, "foo.xml")
    foo.insertDbEntry()
    
    os.environ['interval'] = '1'
    bar = SourceData(src, 3e-7, 2e-7, "bar.xml")
    bar.insertDbEntry()

    os.environ['interval'] = '2'
    foobar = SourceData(src, 1e-7, 1e-7, "foobar.xml")
    foobar.insertDbEntry()
