"""
@brief Move a file to xrootd using the staging code.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import shutil
from FileStager import FileStager

def moveToXrootd(infile, output_dir):
    xrootdGlast = 'root://glast-rdr.slac.stanford.edu//glast'
    xrootd_folder = os.environ['xrootd_folder']
    pipeline_server = os.environ['PIPELINESERVER']
    xrootd_dir = os.path.join(xrootdGlast, xrootd_folder.strip('/'),
                              pipeline_server)

    process_id = os.environ['PIPELINE_PROCESSINSTANCE']
    fileStager = FileStager(process_id, stageArea=output_dir)

    basename = os.path.basename(infile)
    outfile = os.path.join(xrootd_dir, basename)
    staged_name = fileStager.output(outfile)

    shutil.move(infile, staged_name)
    fileStager.finish()
    return outfile
