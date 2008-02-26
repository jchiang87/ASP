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

def getMonitoringEband(emin=100, emax=300000):
    sql = ("select eband_id from ENERGYBANDS where emin=%i and emax=%i"
           % (emin, emax))
    def getEband(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, getEband)

_monitoringBand = getMonitoringBand()

class SourceData(object):
    _upperThreshold = 2e-6
    _lowerThreshold = 2e-7
    def __init__(self, name, srcModel, emin, emax, 
                 flux, fluxerr, srctype, isUL=False):
        self.name = name
        self.srcModel = srcModel
        self.emin, self.emax = emin, emax
        self.flux, self.fluxerr = flux, fluxerr
        self.type = srctype
        self.isUL = isUL
        try:
            self.eband_id = os.environ['eband_id']
        except OSError, message:
            print message
            print "SourceData: eband_id env var not set"
            print ("Setting eband_id to " + _monitoringBand + 
                   " for 100 MeV to 300 GeV")
            self.eband_id = _monitoringBand
        self.interval_number = os.environ['interval_number']
        self.frequency = os.environ['frequency']
    def monitoredState(self):
        """On daily time scales, the monitored state of a non-DRP source
        depends only on the current flux and its state in the previous
        interval in the 100 MeV to 300 GeV band. According to the DRP, we
        only care about this value for daily and weekly monitoring."""
        if (self.type == "DRP" 
            or (self.flux > self._upperThreshold and not self.isUL)):
            return True
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
               "TSTART >= %i and " % os.environ['TSTART'] +
               "TSTOP <= %i" % os.environ['TSTOP'])
        def getIntervals(cursor):
            intervals = [entry[0] for entry in cursor]
            # These should be continguous, so just need endpoints.
            return min(intervals), max(intervals)
        ilims = dbAccess.apply(sql, getIntervals)
        sql = ("select IS_MONITORED from LIGHTCURVES where " +
               "PTSRC_NAME = '%s' and " % self.name + 
               "EBAND_ID = %i and " % _monitoringBand +
               "FREQUENCY = 'daily' and " +
               "INTERVAL_NUMBER <= %i and INTERVAL_NUMBER >= %i" % ilims)
        def getState(cursor):
            for entry in cursor:
                if entry[0]:
                    return True
            return False
        return dbAccess.apply(sql, getState)
    def _monitoredBandState(self):
        if self.flux < self._lowerThreshold or self.isUL:
            return False
        # Use the current flux value and the previous is_monitored
        # state to compute the current is_monitored state
        previous_interval = int(self.interval_number) - 1
        sql = ("select IS_MONITORED from LIGHTCURVES WHERE " +
               "PTSRC_NAME='%s' and " % src.name +
               "EBAND_ID=%i and " % _monitoringBand + 
               "INTERVAL_NUMBER=%i and " % previous_interval +
               "FREQUENCY='daily'")
        def getState(cursor):
            for entry in cursor:
                return entry[0]
        previous_state = dbAccess.apply(sql, getState)
        if (previous_state and not self.isUL 
            and self.flux > self._lowerThreshold):
            return True
        else:
            return False
    def insertDbEntry(self):
        eband_id = 
        interval_number = os.environ['interval']
        frequency = os.environ['frequency']
        sql = (("insert into LIGHTCURVES (PTRSRC_NAME, EBAND_ID, " +
                "INTERVAL_NUMBER, FREQUENCY, FLUX, ERROR, IS_UPPER_LIMIT, " +
                "IS_MONITORED, IS_FLARING, XMLFILE) values ('%s', %s, " +
                "%s, '%s', %e, %e, %i, %i, %i, '%s')")
               % (self.name, eband_id, interval_number, frequency,
                  self.flux, self.fluxerr, int(self.isUL), int(

    def updateDbEntry(self):
        variable = "flux_%i_%i" % (self.emin, self.emax)
        dbEntry = DbEntry(self.name, variable, pars['start_time'],
                          pars['stop_time'])
        dbEntry.setValues(self.flux, self.fluxerr, isUpperLimit=self.isUL)
        dbEntry.setXmlFile(self.srcModel)
        dbEntry.write()
        print "Writing database entry for %s." % self.name
        print "%s = %e +/- %e" % (variable, self.flux, self.fluxerr)
        print "time period: %s to %s" % (pars['start_time'], pars['stop_time'])

