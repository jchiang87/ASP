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
from ft1merge import ft2merge, ft1_filter_merge
from parfile_parser import Parfile
from PipelineCommand import resolve_nfs_path
import drpDbAccess
import databaseAccess as dbAccess
from pass_version import EventClassSelection

def create_parfile(tstart, parfilename='drp_pars.txt'):
    infile = os.path.join(resolve_nfs_path(os.environ['DRPMONITORINGROOT']), 
                          'data', parfilename)
    try:
        shutil.copy(infile, 'drp_pars.txt')
    except IOError:
        infile =os.path.join(resolve_nfs_path(os.environ['DRPMONITORINGROOT']), 
                             'data', 'drpMonitoring', parfilename)
        shutil.copy(infile, 'drp_pars.txt')

    sql = "select startdate, enddate, irfs, ft1_filter from SOURCEMONITORINGCONFIG"
    def findConfig(cursor):
        for entry in cursor:
            startdate, enddate = entry[0], entry[1]
            if startdate <= tstart and tstart <= enddate:
                return entry[2], entry[3]
        message = 'SourceMonitoring configuration not found for %i MET' % tstart
        raise RuntimeError, message
    irfs, ft1_filter = dbAccess.apply(sql, findConfig)
    pars = Parfile(parfilename)
    pars['rspfunc'] = irfs
    pars['ft1_filter'] = ft1_filter
    pars.write()
    return pars

debug = False

#
# Copy the pgwave source list file to the output directory.
#
shutil.copy('pgwaveFileList', os.environ['OUTPUTDIR'])

output_dir = os.environ['OUTPUTDIR']
process_id = os.environ['PIPELINE_PROCESSINSTANCE']
fileStager = FileStager(process_id, stageArea=output_dir)

ft1, ft2 = getStagedFitsData(fileStager=fileStager)

os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

pars = create_parfile(start_time)

gtselect = GtApp('gtselect')

print "Using downlink files: ", ft1

ft1Merged = 'FT1_merged.fits'

#
# Get emin, emax for all bands in GROUP_ID=0
#
ebands = dbAccess.apply('select emin, emax from ENERGYBANDS where GROUP_ID=0',
                        lambda curs: [x for x in curs])
emin = min([x[0] for x in ebands])
emax = max([x[1] for x in ebands])

#
# Prefilter on zenith angle to get rid of most of albedo photons before
# merging. Additional cuts will be applied downstream.
#
ft1_filter_merge(ft1, ft1Merged, zmax=105)

ft2Merged = 'FT2_merged.fits'
ft2merge(ft2, ft2Merged)

gtselect['infile'] = ft1Merged
gtselect['outfile'] = 'temp_filtered.fits'
gtselect['tmin'] = start_time
gtselect['tmax'] = stop_time
gtselect['rad'] = 180.
gtselect['zmax'] = pars['zenmax']
gtselect['emin'] = emin
gtselect['emax'] = emax
evclass = EventClassSelection(ft1Merged)
gtselect['evclass'] = evclass.source

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
pars['ft2file'] = resolve_nfs_path(os.path.abspath(ft2Merged))
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars.write()

drpDbAccess.readRois()

#
# This should be called by FileStager.__del__, but it seems not to be, so...
#
fileStager.finish()

os.system('chmod 777 *')
