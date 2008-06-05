"""
@file makeDrpLcTables.py

@brief Create the FITS tables to contain the light curve information
on the DRP and flaring souces.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import datetime
import numpy as num
import pyfits
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
                try:
                    myData[entry[1]][entry[0]] = (int(entry[2]), int(entry[3]))
                except KeyError:
                    # Do nothing for non-standard frequencies.
                    pass
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
        self.ts = {}
        self.ul = {}
    def addMeasurement(self, entry):
        eband = entry[1]
        self.flux[eband] = entry[4]
        self.error[eband] = entry[5]
        self.ts[eband] = entry[6]
        self.ul[eband] = entry[7]
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
           "FLUX, ERROR, TEST_STATISTIC, IS_UPPER_LIMIT from LIGHTCURVES")
    def getFluxes(cursor):
        fluxes = Fluxes(timeIntervals, ptsrcs, tbounds)
        for entry in cursor:
            fluxes.ingest(entry)
        return fluxes
    return dbAccess.apply(sql, getFluxes)

def extractArray(fluxes, attr):
    return [eval(x.attr) for x in fluxes]

class OrderedDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.ordered_keys = []
    def __setitem__(self, key, value):
        self.ordered_keys.append(key)
        dict.__setitem__(self, key, value)

class FitsTemplate(object):
    def __init__(self, templateFile=None):
        if templateFile is None:
            templateFile = os.path.join(os.environ['DRPMONITORINGROOT'],
                                        'data', 'ASP_light_curves.tpl')
            input = open(templateFile, 'r')
            PHDUKeys = self._readHDU(input)
            self.LCHDU = self._readHDU(input)
        self.HDUList = pyfits.HDUList()
        self.HDUList.append(pyfits.PrimaryHDU())
        self._fillKeywords(self.HDUList[0], PHDUKeys)
    def readDbTables(self, tmin, tmax):
        ptsrcs = drpDbAccess.findPointSources(0, 0, 180)
        timeIntervals = TimeIntervals()
        fluxes = getLightCurves(timeIntervals, ptsrcs, (tmin, tmax))
        flux_list = fluxes.values()
        extract = lambda attr : num.array([eval('x.%s' % attr) for x in 
                                           flux_list])
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

        tstart = extract("tstart")
        start = pyfits.Column(name="START", format="D", unit='S', array=tstart)

        tstop = extract("tstop")
        stop = pyfits.Column(name="STOP", format="D", unit='S', array=tstop)

        names = pyfits.Column(name="NAME", format='20A', 
                              array=extract("name"))

        ras = pyfits.Column(name="RA", format='E', unit='DEGREES',
                            array=extract("ra"))

        decs = pyfits.Column(name="DEC", format='E', unit='DEGREES',
                             array=extract("dec"))

        columns = [start, stop, names, ras, decs]
        for i, band in enumerate(ebands):
            columns.append(pyfits.Column(name="FLUX%s" % band, format="E",
                                         unit="photons/cm^2/s",
                                         array=eband_info("flux", i)))
            columns.append(pyfits.Column(name="ERROR%s" % band, format="E", 
                                         unit="photons/cm^2/s", 
                                         array=eband_info("error", i)))
            columns.append(pyfits.Column(name="UL%s" % band, format="L", 
                                         array=eband_info("ul", i)))

        duration = pyfits.Column(name="DURATION", format="E", unit='S',
                                 array=tstop-tstart)

        ts = pyfits.Column(name="TEST_STATISTIC", format="E",
                           array=eband_info("ts", len(ebands)-1))

        columns.extend([duration, ts])

        self.HDUList.append(pyfits.new_table(columns))
        self.HDUList[1].name = 'LIGHTCURVES'
        self._fillKeywords(self.HDUList[1], self.LCHDU)
    def writeto(self, outfile, clobber=True):
        filename = os.path.basename(outfile)
        self.HDUList[0].header.update('FILENAME', filename)
        self.HDUList[1].header.update('FILENAME', filename)
        self.HDUList.writeto(outfile, clobber=clobber)
    def __getattr__(self, attrname):
        return getattr(self.HDUList, attrname)
    def _fillKeywords(self, hdu, header):
        for key in header.ordered_keys:
            if not hdu.header.has_key(key):
                hdu.header.update(key, header[key][0], comment=header[key][1])
            else: # just append comment
                hdu.header.update(key, hdu.header[key], comment=header[key][1])
        self._fillDate(hdu)
        self._fillCreator(hdu)
    def _fillDate(self, hdu):
        now = datetime.datetime.utcnow()
        date = ("%4i-%02i-%02iT%02i:%02i:%02i" % 
                (now.year, now.month, now.day,now.hour, now.minute, now.second))
        hdu.header.update("DATE", date)
    def _fillCreator(self, hdu):
        version = os.environ['DRPMONITORINGROOT'].split('/')[-1]
        hdu.header.update("CREATOR", "ASP/drpMonitoring %s" % version)
    def _readHDU(self, input):
        my_dict = OrderedDict()
        for line in input:
            if line.find('END') == 0:
                break
            if (line.find('COMMENT') == 0 or 
                line.find('HISTORY') == 0 or
                line.find('#') == 0):
                continue
            try:
                key, value, comment = self._parseLine(line)
                my_dict[key] = value, comment
            except IndexError:
                # skip blank lines
                pass
        return my_dict
    def _parseLine(self, line):
        data = line.split('=')
        key = data[0].strip()
        data2 = data[1].split('/')
        my_value = data2[0].strip()
        comment = ' '.join(data2[1:]).strip()
        if my_value in ('T', 'F'):
            value = {'T' : True, 'F' : False}[my_value]
        else:
            try:
                try:
                    value = int(my_value)
                except ValueError:
                    value = float(my_value)
            except:
                value = my_value.strip("'")
        return key, value, comment

if __name__ == '__main__':
    from GtApp import GtApp

    outfile = 'bar.fits'

    output = FitsTemplate()
    tmin, tmax = 0, 86400*7
    output.readDbTables(tmin, tmax)
    output.writeto(outfile, clobber=True)
    
    fchecksum = GtApp('fchecksum')
    fchecksum.run(infile=outfile, update='yes', datasum='yes', chatter=0)