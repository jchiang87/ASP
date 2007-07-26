"""
@brief Compute the bounds for gtexpmap submaps, read and write them to
a text file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
import pyfits

_defaultTextFile = "gtexpmap_submaps.txt"

def pixbounds(npts, nx):
    x = range(0, npts, npts/nx)
    x.append(npts)
    return x

def writeExpMapBounds(gtexpmap, nx=2, ny=2, textfile=_defaultTextFile):
    xvals = pixbounds(gtexpmap["nlong"], nx)
    yvals = pixbounds(gtexpmap["nlat"], ny)
    output = open(textfile, "w")
    i = 0
    outfile_root = gtexpmap["outfile"].split(".fits")[0]
    for xmin, xmax in zip(xvals[:-1], xvals[1:]):
        for ymin, ymax in zip(yvals[:-1], yvals[1:]):
            outfile = "%s_%02i.fits" % (outfile_root, i)
            output.write("%s  %i  %i  %i  %i\n" %
                         (outfile, xmin, xmax, ymin, ymax))
            i += 1
    output.close()

class ExpMapBounds(object):
    def __init__(self, line):
        data = line.split()
        self.filename = data[0]
        self.xmin, self.xmax, self.ymin, self.ymax = [int(x) for x in data[1:]]

def readExpMapBounds(textfile=_defaultTextFile):
    bounds = []
    input = open(textfile)
    for line in input:
        bounds.append(ExpMapBounds(line))
    return bounds

def combineExpMaps(textfile=_defaultTextFile, outfile="expMap_sum.fits"):
    bounds = readExpMapBounds(textfile)
    infiles = [x.filename for x in bounds]
    expMap = pyfits.open(infiles[0])
    for item in infiles[1:]:
        foo = pyfits.open(item)
        expMap[0].data += foo[0].data
    expMap.writeto(outfile, clobber=True)

if __name__ == '__main__':
    import os
    from parfile_parser import Parfile
    os.chdir(os.environ['OUTPUTDIR'])
    gtexpmap = GtApp('gtexpmap', 'Likelihood')
    grbName = Parfile(os.environ['GRBPARS'])['name']
    outfile = 'expMap_' + grbName + '.fits'
    combineExpMaps(outfile=outfile)
