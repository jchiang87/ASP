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

def get_tbounds(ft1file, tmpfile = 'foo.fits'):
    subprocess.call('xrdcp %s %s' % (ft1file, tmpfile), shell=True)
    ft1 = pyfits.open(tmpfile)
    header = ft1['EVENTS'].header
    tstart, tstop = int(header['TSTART']), int(header['TSTOP'])
    os.remove(tmpfile)
    return tstart, tstop

ft1_fileList = [x.strip() for x in open(os.environ['ft1_fileList'])
                if x.find('#') != 0]
ft2_fileList = [x.strip() for x in open(os.environ['ft2_fileList'])
                if x.find('#') != 0]
ext_fileList = [x.strip() for x in open(os.environ['ext_fileList'])
                if x.find('#') != 0]

fileEntry = int(os.environ['fileEntry'])

tstart, tstop = get_tbounds(ft1_fileList[fileEntry])

pipeline.setVariable("ft1_fileName", ft1_fileList[fileEntry])
pipeline.setVariable("ft2_fileName", ft2_fileList[fileEntry])
pipeline.setVariable("ext_fileName", ext_fileList[fileEntry])

pipeline.setVariable("nDownlink", tstart)
pipeline.setVariable("tstart", tstart)
pipeline.setVariable("tstop", tstop)
