"""
@file checkLevelOneFiles.py

@brief Check the coverage of the Level 1 files for a given time
interval and determine if the task(s) associated with that interval
should be launched.

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
    "Join consecutive intervals that have matching end points."
    bar = [intervals[0]]
    for xx in intervals[1:]:
        if bar[-1][1] == xx[0]:
            bar[-1][1] = xx[1]
        else:
            bar.append(xx)
    return bar

def check_ft2(gtis, ft2):
    """Ensure that the GTIs are contained within contiguous intervals
    covered by the FT2 files."""
    if not ft2:       # an empty set of files cannot cover the gtis
        return False
    tbounds = []
    for item in ft2:
        foo = pyfits.open(item)
        tbounds.append( (int(foo[0].header['TSTART']),
                         int(foo[0].header['TSTOP'])) )
    tbounds.sort()
    tbounds = consolidate(tbounds)
    for tmin, tmax in zip(gtis.START, gtis.STOP):
        covered = False
        for tbound in tbounds:
            if tbound[0] <= tmin and tmax <= tbound[1]:
                covered = True
        if not covered:
            raise RuntimeError, "FT2 files do not cover the FT1 data"
    return True

def providesCoverage(tstart, tstop, min_frac=0.70, ft1List='Ft1FileList',
                     ft2List='Ft1FileList'):
    """Ensure the FT2 files cover the desired GTIs and compute the
    fraction of the elapsed time that is covered by the GTIs.  Return
    False if the desired minumum fractional coverage is not
    achieved."""
    print "providesCoverage: cwd = ", os.path.abspath(os.curdir)
    ft1, ft2 = getFitsData(ft1List, ft2List)
    gtis = FitsNTuple(ft1, 'GTI')
    check_ft2(gtis, ft2)
    if tstart >= min(gtis.START) and tstop <= max(gtis.STOP):
        total = 0
        for tmin, tmax in zip(gtis.START, gtis.STOP):
            total += tmax - tmin
        if total/(tstop - tstart) > min_frac:
            return True
    return False
