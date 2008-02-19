"""
@file aspLauncher.py

@brief Check coverage of FT1/2 files for the desired time intervals and
launch the ASP pipeline tasks corresponding to those intervals.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import pyfits
from FitsNTuple import FitsNTuple
from getFitsData import getFitsData

def consolidate(intervals):
    bar = [intervals[0]]
    for xx in intervals[1:]:
        if bar[-1][1] == xx[0]:
            bar[-1][1] = xx[1]
        else:
            bar.append(xx)
    return bar

def check_ft2(gtis, ft2):
    tbounds = []
    for item in ft2:
        foo = pyfits.open(item)
        tbounds.append( (int(foo[0].header['TSTART']),
                         int(foo[0].header['TSTOP'])) )
    tbounds = consolidate(tbounds)
    for tmin, tmax in zip(gtis.START, gtis.STOP):
        covered = False
        for tbound in tbounds:
            if tbound[0] <= tmin and tmax <= tbound[1]:
                covered = True
        if not covered:
            raise RuntimeError, "FT2 files do not cover the FT1 data"
    return True

def providesCoverage(tstart, tstop, min_frac=0.70, requireFt2=True):
    ft1, ft2 = getFitsData()
    gtis = FitsNTuple(ft1, 'GTI')
    if requireFt2:
        check_ft2(gtis, ft2)
    if tstart >= min(gtis.START) and tstop <= max(gtis.STOP):
        total = 0
        for tmin, tmax in zip(gtis.START, gtis.STOP):
            total += tmax - tmin
        if total/(tstop - tstart) > min_frac:
            return True
    return False

if __name__ == '__main__':
    #




    import glob
    print consolidate(([0, 10], [11., 20], [20., 30]))

    ft1 = glob.glob('test[2]_events*.fits')
    gtis = FitsNTuple(ft1, 'GTI')
    print gtis.START, gtis.STOP
    ft2 = ('test_scData_0000.fits', 'test2_scData_0000.fits')
    print check_ft2(gtis, ft2)
    
    print providesCoverage()
    
