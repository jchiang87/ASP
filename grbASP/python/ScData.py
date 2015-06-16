"""
@brief Encapsulation of spacecraft data.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import bisect
import numpy as num
from FitsNTuple import FitsNTuple
from pyASP import SkyDir

class ScData(object):
    def __init__(self, ft2File):
        self.ft2File = ft2File
        self.scData = FitsNTuple(ft2File, 'SC_DATA')
    def _indx(self, met):
        return bisect.bisect(self.scData.START, met) - 1
    def zaxis(self, met):
        indx = self._indx(met)
        return SkyDir(self.scData.RA_SCZ[indx], self.scData.DEC_SCZ[indx])
    def xaxis(self, met):
        indx = self._indx(met)
        return SkyDir(self.scData.RA_SCX[indx], self.scData.DEC_SCX[indx])
    def yaxis(self, met):
        xaxis = self.xaxis(met)
        zaxis = self.zaxis(met)
        return zaxis.cross(xaxis)
    def inclination(self, met, srcDir):
        return self.zaxis(met).difference(srcDir)*180./num.pi
    def azimuth(self, met, srcDir):
        xaxis = self.xaxis(met)
        yaxis = self.yaxis(met)
        phi = num.arctan2(yaxis.dot(srcDir), xaxis.dot(srcDir))*180./num.pi
        return phi

if __name__ == '__main__':
    _ft2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'
    foo = FitsNTuple(_ft2File)

    scData = ScData(_ft2File)

    for i, met in zip(range(100), foo.START):
        sc_dir = scData.zaxis(met)
        print foo.RA_SCZ[i], foo.DEC_SCZ[i], sc_dir.ra(), sc_dir.dec()
