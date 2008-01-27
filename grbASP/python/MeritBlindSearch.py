"""
@brief Apply blind search algorithm to merit tuples.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

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

class GrbConfig(object):
    PARTITIONSIZE = 20
    DEADTIME = 1000
    THRESHOLD = 112

filter = "((GltWord&10)>0) && ((GltWord&7)!=3) && (FilterStatus_HI==0) && (CTBClassLevel>0) && (CTBBestEnergyProb>0.1) && (CTBCORE>0.1) && (CTBBestEnergy>10) && (CTBBestEnergyRatio<5)"

#merit_file = "root://glast-rdr//glast/mc/ServiceChallenge/GRBgrid-GR-v11r17/merit/GRBgrid-GR-v11r17-000000-merit.root"

merit_file = os.environ['MERITFILE']

raw_events = RootNTuple(merit_file, filter, verbose=True)

gtis = [(min(raw_events.TIME), max(raw_events.TIME))]

raw_events = zenmax_filter(raw_events)

clusterAlg = EventClusters(gtis)

imins, imaxs = gti_bounds(raw_events, gtis)

package = PackagedEvents(raw_events)

grbConfig = GrbConfig()

for imin, imax in zip(imins, imaxs):
    events = package(imin, imax)

    blindSearch = BlindSearch(events, clusterAlg, 
                              dn=grbConfig.PARTITIONSIZE,
                              deadtime=grbConfig.DEADTIME, 
                              threshold=grbConfig.THRESHOLD)

    grbDirs = blindSearch.grbDirs()
    for item in grbDirs:
        grb_dir, tpeak = item
        print grb_dir.ra(), grb_dir.dec(), tpeak
        pass

    output = open("logLike.dat", "w")
    for tt, logdist, logdt in zip(blindSearch.times, blindSearch.logdists,
                                  blindSearch.logdts):
        output.write("%e  %e  %e\n" % (tt, logdist, logdt))
    output.close()
