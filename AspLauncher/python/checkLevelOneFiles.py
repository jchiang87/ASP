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
from getFitsData import getFitsData, getStagedFitsData

def consolidate(intervals):
    "Join consecutive intervals that have matching end points."
    bar = [intervals[0]]
    for xx in intervals[1:]:
        if bar[-1][1] == xx[0]:
            bar[-1][1] = xx[1]
        else:
            bar.append(xx)
    return bar

def isCovered(tstart, tstop, tbounds, slop=0.1):
    """Check if the time interval (tstart, tstop) is contained within a
    contiguous interval contained in the tbounds sequence."""
    for interval in tbounds:
        if interval[0] <= tstart+slop and tstop-slop <= interval[1]:
            return True
    return False

def check_ft2(gtis, ft2):
    """Ensure that the GTIs are contained within contiguous intervals
    covered by the FT2 files."""
    if not ft2:       # an empty set of files cannot cover the gtis
        raise RuntimeError, "FT2 file list is empty"
    tbounds = []
    for item in ft2:
        scData = FitsNTuple(item)
        tbounds.append((min(scData.START), max(scData.STOP)))
    tbounds.sort()
    tbounds = consolidate(tbounds)
    print "ranges of FT2 data:", tbounds
    print "ranges of FT1 data:", gtis.START, gtis.STOP
    for tstart, tstop in zip(gtis.START, gtis.STOP):
        if not isCovered(tstart, tstop, tbounds):
            print tstart, tstop
            raise RuntimeError, "FT2 files do not cover the FT1 data"

def providesCoverage(tstart, tstop, min_frac=0.70, ft1List='Ft1FileList',
                     ft2List='Ft1FileList', fileStager=None):
    """Ensure the FT2 files cover the desired GTIs and compute the
    fraction of the elapsed time that is covered by the GTIs.  Return
    False if the desired minumum fractional coverage is not
    achieved."""
    print "cwd = ", os.path.abspath(os.curdir)
    if fileStager is None:
        ft1, ft2 = getFitsData(ft1List, ft2List, copylist=False)
    else:
        ft1, ft2 = getStagedFitsData(ft1List, ft2List, fileStager=fileStager)
    if not ft1 or not ft2:  # at least one file list is empty
        return False
    gtis = FitsNTuple(ft1, 'GTI')
    try:
        check_ft2(gtis, ft2)
    except RuntimeError, message:
        print "WARNING"
        print message
        print 'gtmktime filter="LIVETIME>0" should be run on these data'
    print "Requested tstart, tstop: ", tstart, tstop
    print "GTI range: ", min(gtis.START), max(gtis.STOP)
    total = 0
    for tmin, tmax in zip(gtis.START, gtis.STOP):
        total += tmax - tmin
    print "Fractional coverage of FT1 files: ", total/(tstop - tstart)
    if total/(tstop - tstart) > min_frac:
        return True
    return False
