"""
@brief Create the FITS tables to contain the light curve information for
the Monitored Source List distributed by the FSSC at
http://fermi.gsfc.nasa.gov/ssc/data/access/lat/msl_lc/

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import datetime
from collections import OrderedDict
import numpy as np
import pyfits
import databaseAccess as dbAccess
from makeDrpLcTables import TimeIntervals, getLastUpdateTime

# This sets the ordering of the columns in the output FITS file.
# The FSSC expects a specific ordering.
_eband_ids = (7, 6, 5)

def get_energy_bands():
    sql = """select energybands.eband_id, energybands.name from energybands
             join taskgrouplist on
             energybands.group_id=taskgrouplist.group_id where
             taskgrouplist.group_name='ASP'"""
    func = lambda curs : dict([(entry[0], entry[1].split('x')[-1])
                                for entry in curs])
    return dbAccess.apply(sql, cursorFunc=func)

def drpNames(aliases=lambda x : x, omit=None):
    sql = """select ptsrc_name from pointsourcetypeset
             where sourcesub_type='DRP'"""
    extract = lambda curs : [aliases(entry[0]) for entry in curs]
    my_names = dbAccess.apply(sql, cursorFunc=extract)
    if omit is not None:
        my_names = [x for x in my_names if x not in omit]
    my_names.sort()
    return my_names

def get_coords():
    sql = """select ptsrc_name, ra, dec from pointsources"""
    func = lambda curs : dict([(entry[0], entry[1:]) for entry in curs])
    return dbAccess.apply(sql, cursorFunc=func)

class FitsEntry(object):
    """Class to manage the data for a single row in the monitored
    source light curve file.  Each row contains flux data for a single
    time interval.  The flux, error and UL information is provided for
    3 energy bands: 100-300000, 300-1000, 1000-300000 MeV."""
    def __init__(self, name, start, stop):
        """Each entry should be uniquely identified by source name and
        the interval start and stop time."""
        self.name = name
        self.start = start
        self.stop = stop
        #
        # Dictionary to hold the flux, error, ul, TS data for each of
        # three energy bands, indexed by eband_id.  Fill with null
        # values so that missing entries are properly set.
        #
        self.data = dict([(id, [-1, -1, -1, -1]) for id in _eband_ids])
    def process_entry(self, entry):
        """Each entry from the LIGHTCURVE db table query contains
        flux, error, ul, TS data for a single energy band."""
        eband_id = entry[-1]
        flux, error, is_ul, ts = entry[:4]
        if ts < 0:
            ts = 0
        self.data[eband_id] = flux, error, is_ul, ts
    def tuple(self, coords):
        """Return the aggregated data as a single tuple so that the
        rows can be zipped into columns for pyfits to write out.
        coords is a dictionary that contains the J2000 coordinates for
        each source by name.  The coordinate info is obtained from the
        POINTSOURCES table."""
        ra, dec = coords[self.name]
        ra, dec = float(ra), float(dec)
        row = [self.start, self.stop, self.name, ra, dec]
        for eband_id in _eband_ids:
            # Append flux, error, is_ul info for each band
            row.extend(self.data[eband_id][:3])
        row.append(float(self.stop - self.start))   # duration
        row.append(self.data[5][-1])         # TS for 100-300000 MeV band
        return tuple(row)

def rename_source(names, old_name, new_name):
    for i in range(len(names)):
        if names[i] == old_name:
            names[i] = new_name
    return names

class LightCurveFitsFile(object):
    def __init__(self, templateFile=None, omit=None,
                 met_filter={'PKS 0502+049' : (0, 430358400),
                             'MG1 J050533+0415' : (0, 430358400)}):
        # The met_filter specifies time ranges that should be omitted.
        # In this case, the FAs requested that data for MG1
        # J050533+0415 prior to Aug 22, 2014 be omitted since that
        # source is now correctly identified as PKS 0502+049.  The
        # filter on PKS 0502+049 is needed to omit fluxes from its
        # ASPJ alias.
        # Entries for MG1 J050533+0415 after Aug 22, 2014 are renamed
        # to PKS 0502+049 in self._add_lightcurve_hdu(...) below and
        # PKS 0502+049 will be fit for instead of MG1 J050533+0415 by 
        # ASP in future DRP runs.
        self.omit = omit
        self.met_filter = met_filter
        if templateFile is None:
            try:
                templateFile = os.path.join(os.environ['DRPMONITORINGROOT'],
                                            'data', 'ASP_light_curves.tpl')
            except KeyError:
                templateFile = os.path.join(os.environ['INST_DIR'],
                                            'data', 'drpMonitoring',
                                            'ASP_light_curves.tpl')
            input = open(templateFile, 'r')
            PHDUKeys = self._readHDU(input)
            self.LCHDU = self._readHDU(input)
        self.HDUList = pyfits.HDUList()
        self.HDUList.append(pyfits.PrimaryHDU())
        self._fillKeywords(self.HDUList[0], PHDUKeys)
    def readDbTables(self, tmin, tmax, chatter=0):
        """Queries of LIGHTCURVES table to obtain the flux info
        for each source.
        """
        time_intervals = TimeIntervals()
        drp_names = drpNames(omit=self.omit)
        results = OrderedDict()
        for i, name in enumerate(drp_names):
            if chatter > 0:
                print i, name
            eband_query = " or ".join(["lightcurves.eband_id=%i" % eband_id
                                       for eband_id in _eband_ids])
            sql = """select
                     lightcurves.flux,
                     lightcurves.error,
                     lightcurves.is_upper_limit,
                     lightcurves.test_statistic,
                     lightcurves.frequency,
                     lightcurves.interval_number,
                     lightcurves.eband_id
                     from lightcurves
                     join pointsources on
                     lightcurves.ptsrc_name=pointsources.ptsrc_name
                     where
                     (%(eband_query)s)
                     and
                     lightcurves.frequency!='six_hours'
                     and
                     (lightcurves.is_monitored=1 or
                      pointsources.is_public=1)
                     and
                     (lightcurves.ptsrc_name='%(name)s' or
                      pointsources.alias='%(name)s')
                     order by lightcurves.frequency asc,
                     lightcurves.interval_number asc,
                     lightcurves.eband_id asc""" % locals()
            if chatter > 2:
                print sql
            func = lambda curs : [entry for entry in curs]
            entries = dbAccess.apply(sql, cursorFunc=func)
            for entry in entries:
                # Time intervals are indexed by frequency and interval_number.
                start, stop = time_intervals(entry[-3], entry[-2])
                if start >= tmax or stop < tmin:
                    continue
                key = name, start, stop
                if name in self.met_filter:
                    filt_tmin, filt_tmax = self.met_filter[name]
                    if start > filt_tmin and stop < filt_tmax:
                        continue
                if not results.has_key(key):
                    results[key] = FitsEntry(*key)
                results[key].process_entry(entry)
        return self._add_lightcurve_hdu(results)
    def _add_lightcurve_hdu(self, results):
        """Add the LIGHTCURVES HDU to the pyfits object."""
        #
        # Collect row-formatted data from each FitsEntry object.
        #
        rows = []
        coords = get_coords()
        for key in results:
            rows.append(results[key].tuple(coords))
        #
        # zip into column format.
        #
        columns = [np.array(col) for col in zip(*rows)]
        #
        # Ad hoc source renaming
        #
        columns[2] = rename_source(columns[2], 
                                   'FERMI J1532-1321 (ATel #3579)',
                                   'TXS 1530-131')
        columns[2] = rename_source(columns[2], 
                                   'MG1 J050533+0415',
                                   'PKS 0502+049')
        #
        # Ensure START, STOP columns are double precision
        #
        columns[0] = np.array(columns[0], dtype=np.float64)
        columns[1] = np.array(columns[1], dtype=np.float64)
        #
        # Set attributes for building pyfits.Columns.
        #
        ebands = get_energy_bands()
        colnames = ["START", "STOP", "NAME", "RA", "DEC"]
        formats = ["D", "D", "30A", "E", "E"]
        units = ["s", "s", None, "deg", "deg"]
        for eband_id in _eband_ids:
            colnames.append("FLUX%s" % ebands[eband_id])
            colnames.append("ERROR%s" % ebands[eband_id])
            colnames.append("UL%s" % ebands[eband_id])
            formats.extend(("E", "E", "L"))
            units.extend(("photons/cm**2/s", "photons/cm**2/s", None))
        colnames.extend(("DURATION", "TEST_STATISTIC"))
        formats.extend(("E", "E"))
        units.extend(("s", None))
        #
        # Create list of pyfits.Columns.
        #
        fits_cols = []
        for colname, format, unit, column in zip(colnames, formats,
                                                 units, columns):
            if unit is not None:
                fits_cols.append(pyfits.Column(name=colname, format=format,
                                               unit=unit, array=column))
            else:
                fits_cols.append(pyfits.Column(name=colname, format=format,
                                               array=column))
        #
        # Add the LIGHTCURVES HDU.
        #
        self.HDUList.append(pyfits.new_table(fits_cols))
        self.HDUList[-1].name = "LIGHTCURVES"
        #
        # Set the header keywords.
        #
        self._fillKeywords(self.HDUList[-1], self.LCHDU)
    def writeto(self, outfile, clobber=True):
        filename = os.path.basename(outfile)
        self.HDUList[0].header.update('FILENAME', filename)
        self.HDUList[1].header.update('FILENAME', filename)
        self.HDUList.writeto(outfile, clobber=clobber)
    def _fillKeywords(self, hdu, header):
        for key in header.keys():
            if not hdu.header.has_key(key):
                hdu.header.update(key, header[key][0], comment=header[key][1])
            else: # just append comment
                hdu.header.update(key, hdu.header[key], comment=header[key][1])
        self._fillDate(hdu)
        self._fillCreator(hdu)
    def _fillDate(self, hdu):
        now = datetime.datetime.utcnow()
        date = ("%4i-%02i-%02iT%02i:%02i:%02i" % 
                (now.year, now.month, now.day,now.hour,now.minute,now.second))
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
    import sys
    from GtApp import GtApp
    import date2met

    os.chdir('/afs/slac/g/glast/ground/links/data/ASP/scratch')

    version = 0

    tmin = 240105600  # 2008 Aug 11
    tmax = getLastUpdateTime()
    print "Most recent processed TSTOP in TIMEINTERVALS table: ", tmax

    #
    # No latency for data release
    #
    latency = 0
    utc_now = date2met.date2met()

    tmax = min(utc_now - latency, tmax)
    print "UTC now minus latency: ", utc_now - latency

    outfile = 'gll_asp_%010i_v%02i.fit' % (tmax, version)

    output = LightCurveFitsFile()

    output.readDbTables(tmin, tmax, chatter=1)
    output.writeto(outfile, clobber=True)
    
    fchecksum = GtApp('fchecksum')
    fchecksum.run(infile=outfile, update='yes', datasum='yes', chatter=0)
