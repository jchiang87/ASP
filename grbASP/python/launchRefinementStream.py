"""
@brief Check for availability of L1 data for a given burst trigger time
       as expressed in a GCN Notice.  If available, launch the 
       GRB_refinement stream.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from FitsNTuple import FitsNTuple
from getFitsData import getStagedFitsData
import dbAccess
from createGrbStreams import refinementStreams

output_dir = os.environ['OUTPUTDIR']
try:
    os.mkdir(output_dir)
    os.chmod(output_dir, 0777)
except OSError:
    if os.path.isdir(output_dir):
        os.chmod(output_dir, 0777)
    else:
        raise OSError, "Error creating directory: " + output_dir

fileStager = FileStager('stagingDir', stageArea=output_dir, 
                        messageLevel='INFO')
ft1, ft2 = getStagedFitsData(fileStager=fileStager)

print 'reading FT1 files:'
for item in ft1:
    print item

gti = FitsNTuple(ft1, 'GTI')

tstart = int(float(os.environ['TSTART']))
tstop = int(float(os.environ['TSTOP']))
grb_id = int(os.environ['GRB_ID'])

print "TSTART, TSTOP =", tstart, tstop
print "min(gti.START), max(gti.STOP) =", min(gti.START), max(gti.STOP)
#if tstart >= min(gti.START) and tstop <= max(gti.STOP):
if True:
    refinementStreams(tstart, tstop, logicalPath=os.environ['logicalPath'],
                      output_dir=output_dir, grb_ids=(grb_id, ),
                      streamId=grb_id, 
                      datacatalog_imp=os.environ['datacatalog_imp'])

fileStager.finish()
