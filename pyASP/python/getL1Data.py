"""
@brief Interface definition and concrete implementation of a function
to fetch L1 data within a given time interval for subsequent analysis.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

_ft2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'
_L1DataPath = '/nfs/farm/g/glast/u33/jchiang/DC2/Downlinks'

_dtime = 10800

_startTime = 220838400.

def getL1Data(tmin, tmax):
    ifile0 = int((tmin - _startTime)/_dtime)
    ifile1 = int((tmax - _startTime)/_dtime)

    ft1Files = []
    for i in range(ifile0, ifile1 + 1):
        ft1Files.append(os.path.join(_L1DataPath, 'downlink_%04i.fits' % i))

    if len(ft1Files) == 0:
        raise LookupError, ("No FT1 files found for METs %s to %s"
                            % (tmin, tmax))
    return tuple(ft1Files), (_ft2File,)

if __name__ == '__main__':
    from FitsNTuple import FitsNTuple
    tmin = _startTime + 32142
    tmax = _startTime + 44213
    ft1, ft2 = getL1Data(tmin, tmax)

    gti = FitsNTuple(ft1[0], 'GTI')
    assert(gti.START[0] < tmin < gti.STOP[-1])

    gti = FitsNTuple(ft1[-1], 'GTI')
    assert(gti.START[0] < tmax < gti.STOP[-1])
