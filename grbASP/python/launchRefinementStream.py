"""
@brief Check for availability of L1 data for a given burst trigger time
       as expressed in a GCN Notice.  If available, launch the 
       GRB_refinement stream.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, sys
from FitsNTuple import FitsNTuple
from getFitsData import getStagedFitsData
import dbAccess
from createGrbStreams import refinementStreams
from FileStager import FileStager
from check_grb_runs import ok_to_launch
from ft1merge import ft1merge, ft2merge
from GtApp import GtApp

output_dir = os.environ['OUTPUTDIR']
try:
    os.mkdir(output_dir)
    os.chmod(output_dir, 0777)
except OSError:
    if os.path.isdir(output_dir):
        os.chmod(output_dir, 0777)
    else:
        raise OSError, "Error creating directory: " + output_dir

tstart = int(float(os.environ['TSTART']))
tstop = int(float(os.environ['TSTOP']))
grb_id = int(os.environ['GRB_ID'])

#
# Use the output from the catalog query and examine the time range
# that is covered.
#
fileStager = FileStager('stagingDir', stageArea=output_dir, 
                        messageLevel='INFO')
ft1, ft2 = getStagedFitsData(fileStager=fileStager)

if not ft1:
    print "No FT1 files returned for the requested time interval. Exiting."
    fileStager.finish()
    sys.exit()

ft1_merged = 'FT1_merged.fits'
ft2_merged = 'FT2_merged.fits'

ft1.sort()
ft2.sort()

ft1merge(ft1, ft1_merged)
ft2merge(ft2, ft2_merged)

gtmktime = GtApp('gtmktime')
gtmktime.run(scfile=ft2_merged, filter='LIVETIME>0', evfile=ft1_merged,
             outfile='filtered.fits')

gti = FitsNTuple('filtered.fits', 'GTI')

is_covered = False
for interval in zip(gti.START, gti.STOP):
    if interval[0] <= tstart and tstop <= interval[1]:
#    if tstop <= interval[1]:
        is_covered = True
        break

if is_covered:
    refinementStreams(tstart, tstop, logicalPath=os.environ['logicalPath'],
                      output_dir=output_dir, grb_ids=(grb_id, ),
                      streamId=grb_id, 
                      datacatalog_imp=os.environ['datacatalog_imp'])

fileStager.finish()

os.remove(ft1_merged)
os.remove(ft2_merged)

#if os.environ['PIPELINESERVER'] == 'PROD':
#    #
#    # In PROD, we can use the info in the RUN table to determine if
#    # the needed runs are available.
#    #
#    runstatus, runs = ok_to_launch((tstart+tstop)/2., (tstop - tstart)/2.)
#
#    if runstatus:
#        refinementStreams(tstart, tstop, logicalPath=os.environ['logicalPath'],
#                          output_dir=output_dir, grb_ids=(grb_id, ),
#                          streamId=grb_id, 
#                          datacatalog_imp=os.environ['datacatalog_imp'])
#else:
#    #
#    # Use the output from the catalog query and examine the time range
#    # that is covered.
#    #
#    fileStager = FileStager('stagingDir', stageArea=output_dir, 
#                            messageLevel='INFO')
#    ft1, ft2 = getStagedFitsData(fileStager=fileStager)
#
#    if not ft1:
#        print "No FT1 files returned for the requested time interval. Exiting."
#        sys.exit()
#
#    print 'reading FT1 files:'
#    for item in ft1:
#        print item
#
#    gti = FitsNTuple(ft1, 'GTI')
#
#    print "TSTART, TSTOP =", tstart, tstop
#    print "min(gti.START), max(gti.STOP) =", min(gti.START), max(gti.STOP)
#
#    if tstart >= min(gti.START) and tstop <= max(gti.STOP):
#        refinementStreams(tstart, tstop, logicalPath=os.environ['logicalPath'],
#                          output_dir=output_dir, grb_ids=(grb_id, ),
#                          streamId=grb_id, 
#                          datacatalog_imp=os.environ['datacatalog_imp'])
#
#    fileStager.finish()
