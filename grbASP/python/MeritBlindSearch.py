"""
@brief Apply blind search algorithm to merit tuples.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import sys
import numarray as num
from BlindSearch import *
from grbASP import RootNTupleBase

_defaultColumns = {'RA' : 'FT1Ra',
                   'DEC' : 'FT1Dec',
                   'TIME' : 'EvtElapsedTime',
                   'ENERGY' : 'FT1Energy',
                   'EVENT_CLASS' : 'CTBClassLevel',
                   'ZENITH_ANGLE' : 'FT1ZenithTheta'}

class RootNTuple(object):
    def __init__(self, meritFile, filter="1", columns=_defaultColumns,
                 verbose=False):
        rt = RootNTupleBase(meritFile)
        rt.readTree(columns.values(), filter, verbose)
        for key in columns:
            self.__dict__[key] = num.array(rt[columns[key]])
        self.names = columns.keys()
        self.EVENT_CLASS = num.array(self.EVENT_CLASS, type=num.Int)

_pass5_cuts = "((GltWord&10)>0) && ((GltWord&7)!=3) && (FilterStatus_HI==0) && (CTBClassLevel>0) && (CTBBestEnergyProb>0.1) && (CTBCORE>0.1) && (CTBBestEnergy>10) && (CTBBestEnergyRatio<5)"

_grbConfig = {'PARTITIONSIZE' : 20,
              'DEADTIME' : 1000,
              'THRESHOLD' : 83}

def process_file(merit_file, cuts=_pass5_cuts, grbConfig=_grbConfig,
                 t0=252460800, logLikeFile='loglike.dat', 
                 output=sys.stdout, columns=_defaultColumns,
                 verbose=False):
    raw_events = RootNTuple(merit_file, cuts, columns=_defaultColumns,
                            verbose=verbose)
    gtis = [(min(raw_events.TIME), max(raw_events.TIME))]
    raw_events = zenmax_filter(raw_events)

    clusterAlg = EventClusters(gtis)
    imins, imaxs = gti_bounds(raw_events, gtis)
    package = PackagedEvents(raw_events)

    for imin, imax in zip(imins, imaxs):
        events = package(imin, imax)
        blindSearch = BlindSearch(events, clusterAlg, 
                                  dn=grbConfig['PARTITIONSIZE'],
                                  deadtime=grbConfig['DEADTIME'], 
                                  threshold=grbConfig['THRESHOLD'])

        grbDirs = blindSearch.grbDirs()
        for item in grbDirs:
            grb_dir, tpeak, ll = item
            output.write("%.3f  %.3f  %.3f  %.3f  %.3f\n" % 
                         (tpeak-t0, tpeak, grb_dir.ra(), grb_dir.dec(), ll))
            output.flush()
            pass

        ll_output = open(logLikeFile, "a")
        for tt, logdist, logdt in zip(blindSearch.times, blindSearch.logdists,
                                      blindSearch.logdts):
            ll_output.write("%e  %e  %e  %e\n" % 
                            (tt-t0, logdist, logdt, logdist + logdt))
            pass
        ll_output.close()

if __name__ == '__main__':
    files = [line.strip() for line in open('filelist.txt')]
    for merit_file in files[93:]:
        process_file(merit_file)
