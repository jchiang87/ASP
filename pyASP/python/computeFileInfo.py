"""
@brief Compute the file information for downlink files and write them
to a text file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import glob
import pyfits
import pipeline

def getObsTimes(ft1File):
    events = pyfits.open(ft1File)["EVENTS"]
    return events.header["TSTART"], events.header["TSTOP"]

filePathRoot = os.environ['filePathRoot']
baseName = os.environ['baseName']

files = glob.glob(os.path.join(filePathRoot, baseName, '*.fits'))
files.sort()

fileList = 'ft1FileList.txt'

output = open(fileList, 'w')
for ft1File in files:
    tstart, tstop = getObsTimes(ft1File)
    output.write('%s  %.3f  %.3f\n' % (ft1File, tstart, tstop))
output.close()

pipeline.setVariable('fileList', fileList)
pipeline.setVariable('numFt1Files', len(files))
