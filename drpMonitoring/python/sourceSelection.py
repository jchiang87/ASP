"""
@file sourceSelection.py
@brief Build source model for all regions-of-interest by reading
       the monitored sources from database tables, and build
       remaining sources using pgwave detections.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from xml.dom import minidom
from read_data import read_data
from readXml import SourceModel, Source
from cleanXml import cleanXml
import databaseAccess as dbAccess
from drpDbAccess import findUniquePointSources, defaultPtSrcXml
from celgal import celgal, dist
from SourceData import _monitoringBand as monitoringBand

def getXmlModel():
    ptsrcs = findUniquePointSources(0, 0, 180)
    xmlModel = """<?xml version="1.0" ?>
<source_library title="Likelihood model">
</source_library>
"""
    doc = minidom.parseString(xmlModel)
    lib = doc.getElementsByTagName('source_library')[0]
    for src in ptsrcs:
        # Skip the 3EG sources; pgwave should find them.
        if src.find('_3EG') != 0: 
            print "adding", src
            lib.appendChild(ptsrcs[src].domElement())
    return cleanXml(doc)

class PgwaveSource(object):
    _converter = celgal()
    def __init__(self, line):
        """This class is extremely dangerous since it relies on
        a fixed format for an ascii file from pgwave.  This format
        seems to change without warning, so this needs to be
        checked against the current version of the pgwave code.
        """
        data = line.split()
        self.id = int(data[0])
        #
        # Need to be careful here.  pgwave .list output had been
        # mislabeled as RA, Dec when it really was l, b.  Now it
        # appears to give correct data.
        #
        self.ra, self.dec = float(data[3]), float(data[4])
        self.l, self.b = self._converter.gal((self.ra, self.dec))
        self.signif = float(data[7])
    def dist(self, xmlsrc):
        ra = xmlsrc.spatialModel.RA.value
        dec = xmlsrc.spatialModel.DEC.value
        return dist((self.ra, self.dec), (ra, dec))

def currentDailyInterval(time):
    sql = ("select INTERVAL_NUMBER from TIMEINTERVALS where " + 
           "TSTART<=%i and %i<=TSTOP and FREQUENCY='daily'" % (time, time))
    print "currentDailyInterval:", sql
    def getIntervalNum(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, getIntervalNum)

def isMonitored(src, interval_time):
    "Return IS_MONITORED flag from the preceeding day."
    currentInterval = currentDailyInterval(interval_time - 8.64e4)
    print "insided isMonitored:", src, interval_time, currentInterval, monitoringBand
    if currentInterval is None:
        return False
    sql = ("select IS_MONITORED from LIGHTCURVES where "
           + "FREQUENCY='daily' and " 
           + "INTERVAL_NUMBER=%i and " % currentInterval
           + "PTSRC_NAME='%s' and " % src
           + "EBAND_ID=%i" % monitoringBand)
    def getFlag(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, getFlag)

def sourceType(src):
    try:
        return src.sourceType
    except AttributeError:
        return 'None'

if __name__ == '__main__':
    os.chdir(os.environ['OUTPUTDIR'])

    pgwaveSrcList = open('pgwaveFileList').readlines()[0].strip().strip('+')

    xmlModel = getXmlModel()

    outfile = "point_sources.xml"
    output = open(outfile, 'w')
    output.write(xmlModel.toxml() + "\n")
    output.close()

    srcModel = SourceModel(outfile)

    pg_srcs = [PgwaveSource(line) for line in open(pgwaveSrcList) 
               if line.find("#")==-1]

    def nearestSource(src, srcModel):
        srcNames = srcModel.names()
        nearest = srcNames[0]
        minsep = src.dist(srcModel[nearest])
        for item in srcNames[1:]:
            sep = src.dist(srcModel[item]) 
            if sep < minsep:
                nearest = item
                minsep = sep
        return nearest, minsep

    # Keep track of all of the found by pgwave, substituting the name
    # from POINTSOURCES when it is within the positional coincidence
    # tolerance.
    pgwave_list = []
    tol = 0.5
    for src in pg_srcs:
        nearest, sep = nearestSource(src, srcModel)
        if sep > tol:  # add this in as a anonymous pgwave source
            name = "pgw_%04i" % src.id
            doc = minidom.parseString(defaultPtSrcXml(name, src.ra, src.dec))
            srcModel[name] = Source(doc.getElementsByTagName('source')[0])
            pgwave_list.append(name)
        else:
            pgwave_list.append(nearest)

    tstart = int(os.environ['TSTART'])
    tstop = int(os.environ['TSTOP'])
#    interval_time = (tstart + tstop)/2.
    interval_time = tstart

    #
    # Loop over sources in model and keep only DRP, pgwave, and monitored
    # sources
    #
    for src in srcModel.names():
        if not (src in pgwave_list or
                sourceType(srcModel[src]) == 'DRP' or
                isMonitored(src, interval_time)):
            del srcModel[src]

    #
    # Limit the photon indices to < -1.5:
    #
    for src in srcModel.names():
        srcModel[src].spectrum.Index.max = -1.5

    srcModel.writeTo('point_sources.xml')
