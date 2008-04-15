"""
@file makeDrpLcTables.py

@brief Create the FITS tables to contain the light curve information
on the DRP and flaring souces.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import drpDbAccess
import databaseAccess as dbAccess

class TimeIntervals(object):
    def __init__(self):
        sql = ("select INTERVAL_NUMBER, FREQUENCY, TSTART, TSTOP " + 
               "from TIMEINTERVALS")
        def getIntervals(cursor):
            myData = {'six_hours' : {},
                      'daily' : {},
                      'weekly' : {}}
            for entry in cursor:
                myData[entry[1]][entry[0]] = (int(entry[2]), int(entry[3]))
            return myData
        self.intervals = dbAccess.apply(sql, getIntervals)
    def __call__(self, freq, interval_num):
        return self.intervals[freq][interval_num]

class EpochData(object):
    def __init__(self, entry, timeIntervals, ptsrcs):
        self.name = entry[0]
        self.tstart, self.tstop = timeIntervals(entry[3], entry[2])
        self.ra, self.dec = ptsrcs[entry[0]].ra, ptsrcs[entry[0]].dec
        self.flux = {}
        self.error = {}
        self.ul = {}
    def addMeasurement(self, entry):
        eband = entry[1]
        self.flux[eband] = entry[4]
        self.error[eband] = entry[5]
        self.ul[eband] = entry[6]
    def accept(self, tbounds):
        return (tbounds[0] <= self.tstart <= tbounds[1] or
                tbounds[0] <= self.tstop <= tbounds[1])

class Fluxes(dict):
    def __init__(self, timeIntervals, ptsrcs, tbounds=None):
        dict.__init__(self)
        self.timeInts, self.ptsrcs = timeIntervals, ptsrcs
        self.tbounds = tbounds
    def ingest(self, entry):
        PK = entry[0], entry[2], entry[3]
        epochData = EpochData(entry, self.timeInts, self.ptsrcs)
        if self.tbounds is None or epochData.accept(self.tbounds):
            if not PK in self.keys():
                self[PK] = epochData
            self[PK].addMeasurement(entry)

def fmcmp(fm1, fm2):
    if (fm1.tstart < fm2.tstart or 
        fm1.tstart==fm2.tstart and fm1.tstop < fm2.tstop):
        return -1
    elif (fm1.tstart > fm2.tstart or 
          fm1.tstart==fm2.tstart and fm1.tstop > fm2.tstop):
        return 1
    else:
        return 0

def getLightCurves(timeIntervals, ptsrcs, tbounds=None):
    sql = ("select PTSRC_NAME, EBAND_ID, INTERVAL_NUMBER, FREQUENCY, " +
           "FLUX, ERROR, IS_UPPER_LIMIT from LIGHTCURVES")
    def getFluxes(cursor):
        fluxes = Fluxes(timeIntervals, ptsrcs, tbounds)
        for entry in cursor:
            fluxes.ingest(entry)
        return fluxes
    return dbAccess.apply(sql, getFluxes)

def extractArray(fluxes, attr):
    return [eval(x.attr) for x in fluxes]

if __name__ == '__main__':
    import numpy as num
    from pyfits import Column, HDUList, PrimaryHDU, new_table

    ptsrcs = drpDbAccess.findPointSources(0, 0, 180)
    timeIntervals = TimeIntervals()
    tbounds = 257731200, 258336000
    fluxes = getLightCurves(timeIntervals, ptsrcs, tbounds)
    flux_list = fluxes.values()
    flux_list.sort(fmcmp)

    extract = lambda attr : num.array([eval('x.%s' % attr) for x in flux_list])
    def eband_info(attr, i):
        data = []
        for item in flux_list:
            foo = item.__dict__[attr]
            try:
                value = foo[i]
            except KeyError:
                value = -1     # null value
            data.append(value)
        return num.array(data)

    ebands = ["_100_300", "_300_1000", "_1000_3000", "_3000_10000", 
              "_10000_300000", "_100_300000"]

    start = Column(name="START", format="D", array=extract("tstart"))
    stop = Column(name="STOP", format="D", array=extract("tstop"))
    names = Column(name="SOURCE", format='20A', array=extract("name"))
    ras = Column(name="RA", format='E', array=extract("ra"))
    decs = Column(name="DEC", format='E', array=extract("dec"))
    columns = [start, stop, names, ras, decs]
    for i, band in enumerate(ebands):
        columns.append(Column(name="FLUX%s" % band, format="E", 
                              array=eband_info("flux", i)))
        columns.append(Column(name="ERROR%s" % band, format="E", 
                              array=eband_info("error", i)))
        columns.append(Column(name="UL%s" % band, format="L", 
                              array=eband_info("ul", i)))

    output = HDUList()
    output.append(PrimaryHDU())
    output.append(new_table(columns))
    output[1].name = "LIGHTCURVES"
    output.writeto('bar.fits', clobber=True)
