"""
@brief Read the FT1 file info from the summary file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import pipeline

fileList = open(os.environ['fileList']).readlines()
fileEntry = int(os.environ['fileEntry'])

filename, tstart, tstop = fileList[fileEntry].split()

pipeline.setVariable("fileName", filename)
pipeline.setVariable("nDownlink", fileEntry)
pipeline.setVariable("tstart", tstart)
pipeline.setVariable("tstop", tstop)

