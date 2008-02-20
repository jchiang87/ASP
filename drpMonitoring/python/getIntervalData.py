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
from getFitsData import getFitsData
from ft1merge import ft1merge
from parfile_parser import Parfile
import drpDbAccess
from drpDbAccess import databaseAccess as dbAccess

def create_parfile(tstart, parfilename='drp_pars.txt'):
    version = os.path.split(os.environ['DRPMONITORINGROOT'])[-1]
    infile = os.path.join(os.environ['ASP_PATH'], 'drpMonitoring', version,
                          'data', parfilename)
    shutil.copy(infile, 'drp_pars.txt')
    sql = "select * from SOURCEMONITORINGCONFIG"
    def findConfig(cursor):
        for entry in cursor:
            startdate, enddate = entry[1], entry[2]
            if startdate <= tstart and tstart <= enddate:
                return entry[3]
        message = 'SourceMonitoring configuration not found for %i MET' % tstart
        raise RuntimeError, message
    irfs = dbAccess.apply(sql, findConfig, dbAccess.glastdev)
    pars = Parfile(parfilename)
    pars['rspfunc'] = irfs
    pars.write()
    return pars

debug = False

ft1, ft2 = getFitsData()

output_dir = os.environ['OUTPUTDIR']
os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

pars = create_parfile(start_time)

gtselect = GtApp('gtselect')

print "Using downlink files: ", ft1

ft1Merged = 'FT1_merged.fits'
ft1merge(ft1, ft1Merged)

outfile = open('Ft2FileList', 'w')
for item in ft2:
    outfile.write('%s\n' % item)
outfile.close()

fmerge = GtApp('fmerge')
fmerge['infiles'] = '@Ft2FileList'
fmerge['outfile'] = 'FT2_merged.fits'
fmerge['clobber'] = 'yes'
fmerge['columns'] = ' '
fmerge['mextname'] = ' '
fmerge['lastkey'] = ' '
fmerge.run()

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
pars['ft2file'] = os.path.abspath(fmerge['outfile'])
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars.write()

drpDbAccess.readRois()

os.system('chmod 777 *')
