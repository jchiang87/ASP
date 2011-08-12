"""
@brief Read the FT1 file info from the summary file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import pyfits
import subprocess
import pipeline

ft1_fileList = []
tstart = []
tstop = []
for line in open(os.environ['ft1_fileList'], 'r'):
    data = line.split()
    ft1_fileList.append(data[0])
    tstart.append(data[1])
    tstop.append(data[2])

ft2_fileList = [x.strip() for x in open(os.environ['ft2_fileList'])
                if x.find('#') != 0]
ext_fileList = [x.strip() for x in open(os.environ['ext_fileList'])
                if x.find('#') != 0]

fileEntry = int(os.environ['fileEntry'])

pipeline.setVariable("ft1_fileName", ft1_fileList[fileEntry])
pipeline.setVariable("ft2_fileName", ft2_fileList[fileEntry])
pipeline.setVariable("ext_fileName", ext_fileList[fileEntry])

pipeline.setVariable("nDownlink", tstart[fileEntry])
pipeline.setVariable("tstart", tstart[fileEntry])
pipeline.setVariable("tstop", tstop[fileEntry])
