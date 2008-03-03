"""
@brief Extract FT1 data for a specified time range given by TSTART and
TSTOP environment variables.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, shutil
from GtApp import GtApp
from FitsNTuple import FitsNTuple
from getFitsData import getStagedFitsData
from FileStager import FileStager
from ft1merge import ft1merge, ft2merge
from parfile_parser import Parfile
import drpDbAccess
import databaseAccess as dbAccess

def create_parfile(tstart, parfilename='drp_pars.txt'):
    version = os.path.split(os.environ['DRPMONITORINGROOT'])[-1]
    infile = os.path.join(os.environ['ASP_PATH'], 'ASP', 'drpMonitoring', 
                          version, 'data', parfilename)
    shutil.copy(infile, 'drp_pars.txt')
    sql = "select * from SOURCEMONITORINGCONFIG"
    def findConfig(cursor):
        for entry in cursor:
            startdate, enddate = entry[1], entry[2]
            if startdate <= tstart and tstart <= enddate:
                return entry[3]
        message = 'SourceMonitoring configuration not found for %i MET' % tstart
        raise RuntimeError, message
    irfs = dbAccess.apply(sql, findConfig)
    pars = Parfile(parfilename)
    pars['rspfunc'] = irfs
    pars.write()
    return pars

debug = False

output_dir = os.environ['OUTPUTDIR']
process_id = os.environ['PIPELINE_PROCESSINSTANCE']
fileStager = FileStager(process_id, stageArea=output_dir, cleanup=False)

ft1, ft2 = getStagedFitsData(fileStager=fileStager)

os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

pars = create_parfile(start_time)

gtselect = GtApp('gtselect')

print "Using downlink files: ", ft1

ft1Merged = 'FT1_merged.fits'
ft1merge(ft1, ft1Merged)

ft2Merged = 'FT2_merged.fits'
ft2merge(ft2, ft2Merged)

gtselect['infile'] = ft1Merged
gtselect['outfile'] = 'temp_filtered.fits'
gtselect['tmin'] = start_time
gtselect['tmax'] = stop_time
gtselect['rad'] = 180.
gtselect['zmax'] = pars['zenmax']

if debug:
    print gtselect.command()
else:
    gtselect.run()

#
# Check to see if any events were selected by the time filter.
#
foo = FitsNTuple(gtselect['outfile'])
if len(foo.TIME) == 0:
    ft1_input = FitsNTuple(ft1Merged)
    message = ("Zero events selected by the time filter.\n" +
               "Input data time range: %i to %i\n" % (ft1_input.TIME[0], 
                                                      ft1_input.TIME[-1]) +
               "Time selection range: %i to %i\n" % (start_time, stop_time))
    raise RuntimeError, message

#
# Use fcopy to apply ft1_filter from par file
#
fcopy = GtApp('fcopy')
fcopy['infile'] = '%s[EVENTS][%s]' % (gtselect['outfile'], pars['ft1_filter'])
fcopy['outfile'] = 'time_filtered_events.fits'
try:
    os.remove(fcopy['outfile'])
except OSError:
    pass

if debug:
    print fcopy.command()
else:
    fcopy.run()

pars['ft1file'] = fcopy['outfile']
pars['ft2file'] = os.path.abspath(ft2Merged)
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars.write()

drpDbAccess.readRois()

#
# Insert the current interval into the TIMEINTERVALS table.
#
inum = int(os.environ['interval'])
frequency = os.environ['frequency']
sql = ("insert into TIMEINTERVALS " +
       "(INTERVAL_NUMBER, FREQUENCY, TSTART, TSTOP) values " +
       "(%i, '%s', %i, %i)" % (inum, frequency, start_time, stop_time))
try:
    dbAccess.apply(sql)
except dbAccess.cx_Oracle.IntegrityError, message:
    #
    # Check to see if this interval is already in the table
    #
    sql = ("select tstart, tstop from TIMEINTERVALS where " +
           "INTERVAL_NUMBER=%i and FREQUENCY='%s'" % (inum, frequency))
    def getTlims(cursor):
        for entry in cursor:
            return entry[0], entry[1]
    tlims = dbAccess.apply(sql, getTlims)
    if tlims[0] != start_time or tlims[1] != stop_time:
        raise dbAccess.cx_Oracle.IntegrityError, message 

os.system('chmod 777 *')
