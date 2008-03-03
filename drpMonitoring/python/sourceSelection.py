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
from drpDbAccess import findPointSources, defaultPtSrcXml
from celgal import celgal, dist

class Roi(object):
    def __init__(self, ra, dec, rad, sr):
        self.ra, self.dec = ra, dec
        self.rad, self.sr = rad, sr

class RoiIds(dict):
    def __init__(self, roiFile='rois.txt'):
        for id, ra, dec, rad, sr in zip(*read_data(roiFile)):
            self[id] = Roi(ra, dec, rad, sr)
    def __call__(self, ra, dec):
        ids = self.keys()
        myId = ids[0]
        mindist = dist((self[myId].ra, self[myId].dec), (ra, dec))
        for id in ids[1:]:
            curDist = dist((self[id].ra, self[id].dec), (ra, dec))
            if curDist < mindist:
                myId = id
                mindist = curDist
        if mindist < self[myId].sr:
            return myId
        return None

roiIds = RoiIds()

def assignNullRois():
    sql = "select PTSRC_NAME, ra, dec from POINTSOURCES where ROI_ID IS NULL"
    srcs = dbAccess.apply(sql, lambda curs : [entry[:3] for entry in curs])
    for src in srcs:
        id = roiIds(src[1], src[2])
        if id is not None:
            sql = ("update POINTSOURCES set ROI_ID=%i where PTSRC_NAME='%s'" 
                   % (id, src[0]))
            dbAccess.apply(sql)

def getXmlModel():
    ptsrcs = findPointSources(0, 0, 180)
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
        data = line.split()
        self.id = int(data[0])
        #
        # Need to be careful here.  pgwave .list output had been
        # mislabeled as RA, Dec when it really was l, b.  Now it
        # appears to give correct data.
        #
        self.ra, self.dec = float(data[3]), float(data[4])
        self.l, self.b = self._converter.gal((self.ra, self.dec))
        self.snr = float(data[5])
    def dist(self, xmlsrc):
        ra = xmlsrc.spatialModel.RA.value
        dec = xmlsrc.spatialModel.DEC.value
        return dist((self.ra, self.dec), (ra, dec))

if __name__ == '__main__':
    os.chdir(os.environ['OUTPUTDIR'])

    # Ensure every source in the POINTSOURCES table has an ROI_ID if
    # it is in a source region.
    assignNullRois()

    pgwaveSrcList = open('pgwaveFileList').readlines()[0].strip().strip('+')

    xmlModel = getXmlModel()

    outfile = "point_sources.xml"
    output = open(outfile, 'w')
    output.write(xmlModel.toxml() + "\n")
    output.close()

    srcModel = SourceModel(outfile)

    pg_srcs = [PgwaveSource(line) for line in open(pgwaveSrcList) 
               if line.find("#")==-1]

    def srcPosCoincidence(src, srcModel, tol=0.5):
        for item in srcModel.names():
            if src.dist(srcModel[item]) < tol:
                return True
        return False

    for src in pg_srcs:
        if not srcPosCoincidence(src, srcModel):
            name = "pgw_%04i" % src.id
            doc = minidom.parseString(defaultPtSrcXml(name, src.ra, src.dec))
            srcModel[name] = Source(doc.getElementsByTagName('source')[0])

    #
    # Limit the photon indices to < -1.5:
    #
    for src in srcModel.names():
        srcModel[src].spectrum.Index.max = -1.5

    srcModel.writeTo('point_sources.xml')
