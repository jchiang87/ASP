"""
@brief Apply blind search algorithm to merit tuples.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import sys
import numpy as num
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
        self.EVENT_CLASS = num.array(self.EVENT_CLASS, dtype=num.int)

_pass5_cuts = "((GltWord&10)>0) && ((GltWord&7)!=3) && (FilterStatus_HI==0) && (CTBClassLevel>0) && (CTBBestEnergyProb>0.1) && (CTBCORE>0.1) && (CTBBestEnergy>10) && (CTBBestEnergyRatio<5)"

_grbConfig = {'PARTITIONSIZE' : 20,
              'DEADTIME' : 1000,
              'THRESHOLD' : 83}

def process_file(merit_file, cuts=_pass5_cuts, grbConfig=_grbConfig,
                 t0=252460800, logLikeFile='loglike.dat', 
                 output=sys.stdout, columns=_defaultColumns,
                 verbose=False):
    if verbose:
        print "using grbConfig:"
        print grbConfig, "\n"
        print "using merit columns:"
        print columns, "\n"
    raw_events = RootNTuple(merit_file, cuts, columns=_defaultColumns,
                            verbose=verbose)
    gtis = [(min(raw_events.TIME), max(raw_events.TIME))]
    try:
        zmax = grbConfig['ZENMAX']
    except:
        zmax = 100
    if verbose:
        print "using ZENMAX = ", zmax
    raw_events = zenmax_filter(raw_events, zmax)

    if verbose:
        print "considering ", len(raw_events.RA), " events"

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

def get_TCut(infile):
    for line in open(infile):
        tcut = ""
        if line.find("#") != 0:
            tcut += line.strip()
    return tcut

if __name__ == '__main__':
    import os
    from parfile_parser import Parfile
    from FileStager import FileStager

    merit_file = os.environ["MERIT_FILE"]
    ds_name = "%05i" % int(os.environ["DS_NAME"])

    try:
        grbConfig = Parfile(os.environ["GRBCONFIG_FILE"])
    except KeyError:
        grbConfig = _grbConfig

    try:
        columns = Parfile(os.environ["COLUMN_FILE"])
    except KeyError:
        columns = _defaultColumns

    try:
        cuts = get_TCut(os.environ["TCUT_FILE"])
    except KeyError:
        cuts = _pass5_cuts
    
    fileStager = FileStager("GRBgrid_blind_search/%s" % ds_name, "INFO")
    outdir = os.path.join(os.environ["output_dir"], ds_name)
    try:
        os.mkdir(outdir)
    except OSError, message:
        print message
        pass
    outpath = lambda x : os.path.join(outdir, x)

    logLikeFile = fileStager.output(outpath("logLike.dat"))
    candidateBurstFile = fileStager.output(outpath("candidateBursts.dat"))

    results = open(candidateBurstFile, "w")
    
    process_file(merit_file, logLikeFile=logLikeFile, output=results,
                 cuts=cuts, grbConfig=grbConfig, columns=columns, 
                 verbose=True)
