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
from getFitsData import getFitsData
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

ft1, ft2 = getFitsData()

gti = FitsNTuple(ft1, 'GTI')

tstart = int(float(os.environ['TSTART']))
tstop = int(float(os.environ['TSTOP']))
grb_id = int(os.environ['GRB_ID'])

if tstart >= min(gti.START) and tstop <= max(gti.STOP):
    dbAccess.updateGrb(grb_id, L1_DATA_AVAILABLE=1)
    refinementStreams(tstart, tstop, logicalPath=os.environ['logicalPath'],
                      output_dir=output_dir, grb_ids=(grb_id, ),
                      streamId=grb_id)
