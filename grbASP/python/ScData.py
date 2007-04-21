"""
@brief Encapsulation of spacecraft data for use by PsfClusters.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import bisect
import numarray as num
from FitsNTuple import FitsNTuple
from pyIrfLoader import SkyDir

_ft2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

class ScData(object):
    def __init__(self, ft2File=_ft2File):
        self.ft2File = ft2File
        self.scData = FitsNTuple(ft2File, 'SC_DATA')
    def zaxis(self, met):
        indx = bisect.bisect(self.scData.START, met) - 1
        return SkyDir(self.scData.RA_SCZ[indx], self.scData.DEC_SCZ[indx])
    def inclination(self, met, srcDir):
        return self.zaxis(met).difference(srcDir)*180./num.pi

if __name__ == '__main__':
    foo = FitsNTuple(_ft2File)

    scData = ScData(_ft2File)

    for i, met in zip(range(100), foo.START):
        sc_dir = scData.zaxis(met)
        print foo.RA_SCZ[i], foo.DEC_SCZ[i], sc_dir.ra(), sc_dir.dec()
