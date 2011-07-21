"""
@brief Retrieve the FT1/2 data from the dataCatalog given a time-based 
query made by the PGWave task.
"""
#
# $Header$
#

import os, shutil
from GtApp import GtApp
from getFitsData import getStagedFitsData
from ft1merge import ft2merge, ft1_filter_merge
from FitsNTuple import FitsNTuple
from FileStager import FileStager
from PipelineCommand import pipelineServer
from pass_version import pass_version

fcopy = GtApp('fcopy')
gtmktime = GtApp('gtmktime')
gtselect = GtApp('gtselect')

def filter_string(ft1file):
    my_filter = "ENERGY > 0"  # do nothing default
    foo = FitsNTuple(ft1file)
    if 'CTBCLASSLEVEL' in foo.names:
        my_filter += " && CTBCLASSLEVEL>1"
    return my_filter

output_dir = os.environ['OUTPUTDIR']
process_id = os.environ['PIPELINE_PROCESSINSTANCE']
fileStager = FileStager(process_id, stageArea=output_dir)

ft1, ft2 = getStagedFitsData(fileStager=fileStager)

os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

print "Using downlink files: ", ft1

ft1Merged ='FT1_merged.fits'
#
# Use do-nothing default filter.
#
ft1_filter_merge(ft1, ft1Merged, filter_string(ft1[0]))

ft2Merged = 'FT2_merged.fits'
ft2merge(ft2, ft2Merged)

gtmktime.run(scfile=ft2Merged, evfile=ft1Merged, outfile='foo.fits', 
             filter="IN_SAA!=T && LIVETIME>0")
shutil.copy('foo.fits', ft1Merged)

gti = FitsNTuple(ft1Merged, 'GTI')

gtselect['infile'] = ft1Merged
gtselect['outfile'] ='time_filtered_events.fits'
gtselect['tmin'] = start_time
gtselect['tmax'] = stop_time
gtselect['ra'] = 180.
gtselect['dec'] = 0.
gtselect['rad'] = 180
gtselect['emin'] = 30
gtselect['emax'] = 3e5
gtselect.run()

try:
    os.remove('Filtered.fits')
except OSError:
    pass

if (pipelineServer() == 'DEV' and 
    os.environ['datacatalog_imp'] != 'datacatalogPROD'):
    os.system('ln -s time_filtered_events.fits Filtered.fits')
else:
    # Prod (flight) data.
    #
    # Perform CTBCLASSLEVEL cut when it is available.  @todo implement
    # to use ft1_filter string from SourceMonitoringConfig table
    #
    #
    foo = FitsNTuple('time_filtered_events.fits', 'EVENTS')
    fcopy = GtApp('fcopy')
    if 'CTBCLASSLEVEL' in foo.names:
        fcopy.run(infile='time_filtered_events.fits[EVENTS][CTBCLASSLEVEL>1]',
                  outfile='Filtered.fits')
    elif 'EVENT_CLASS' in foo.names:
        if pass_version('time_filtered_events.fits') != 'NONE':
            fcopy.run(infile='time_filtered_events.fits[EVENTS][EVENT_CLASS>1]',
                      outfile='Filtered.fits')
        else:
            # For Pass 7, apply Source class selection
            gtselect.run(infile='time_filtered_events.fits',
                         outfile='Filtered.fits',
                         evclass=2)

#
# apply zenith angle cut and energy cut
#
gtselect.run(emin=100, zmax=105, infile='Filtered.fits',
             outfile='Filtered_evt.fits')

import databaseAccess as dbAccess

#
# Set the is_processed flag for this interval
#
interval = int(os.environ['interval'])
frequency = os.environ['frequency']

sql = ("update TIMEINTERVALS set IS_PROCESSED=1 where " +
       "INTERVAL_NUMBER=%i and " % interval +
       "FREQUENCY='%s'" % frequency)
try:
    dbAccess.apply(sql)
except StandardError, message:
    print message
    print sql

os.system('chmod 777 *')
