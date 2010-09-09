"""
@brief Check for availability of L1 data for a given burst trigger time
       as expressed in a GCN Notice.  If available, launch the 
       GRB_afterglow stream.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from FitsNTuple import FitsNTuple
from getFitsData import getStagedFitsData
from createGrbStreams import afterglowStreams
from FileStager import FileStager

output_dir = os.environ['OUTPUTDIR']

fileStager = FileStager('stagingDir', stageArea=output_dir, 
                        messageLevel='INFO')
ft1, ft2 = getStagedFitsData(fileStager=fileStager)

gti = FitsNTuple(ft1, 'GTI')

tstart = int(os.environ['TSTART'])
tstop = int(os.environ['TSTOP'])
grb_id = int(os.environ['GRB_ID'])

if tstart >= min(gti.START) and tstop <= max(gti.STOP):
    afterglowStreams(logicalPath=os.environ['logicalPath'],
                     output_dir=output_dir, streamId=grb_id,
                     datacatalog_imp=os.environ['datacatalog_imp'])

fileStager.finish()
