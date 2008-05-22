"""
@brief Assign ROIS.  Use db table rois for DRP and other monitored sources.
Generate ROIs for other sources found by pgwave.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
from read_data import read_data
import databaseAccess as dbAccess
from celgal import dist

class Roi(object):
    def __init__(self, ra, dec, rad, sr):
        self.ra, self.dec = ra, dec
        self.rad, self.sr = rad, sr
        self.srcCoords = {}
    def __repr__(self):
        return "%7.3f  %7.3f  %i  %i" % (self.ra, self.dec, self.rad, self.sr)

class RoiIds(dict):
    def __init__(self, infile=None):
        if infile is None:
            sql = "select ROI_ID, RA, DEC, RADIUS, SR_RADIUS from ROIS"
            def readRoiTable(cursor):
                for item in cursor:
                    self[item[0]] = Roi(*item[1:])
            dbAccess.apply(sql, readRoiTable)
        else:
            data = read_data(infile)
            for line in zip(*data):
                self[line[0]] = Roi(*line[1:])
    def __call__(self, ra, dec, offset=3):
        """Return the ROI with center closest to the given sky coordinate.
        The minimum distance from the ROI center for identifying a
        valid ROI for a source at this location is roi_rad - offset"""
        ids = self.keys()
        myId = ids[0]
        mindist = dist((self[myId].ra, self[myId].dec), (ra, dec))
        for id in ids[1:]:
            curDist = dist((self[id].ra, self[id].dec), (ra, dec))
            if curDist < mindist:
                myId = id
                mindist = curDist
        if mindist < self[myId].rad - offset:
            # save source coords to keep track of number of sources
            self[myId].srcCoords[(ra, dec)] = 1
            return myId
        return None
    def write(self, outfile, prune=True):
        output = open(outfile, 'w')
        ids = self.keys()
        ids.sort()
        for id in ids:
            if not prune or self[id].srcCoords.keys():
                output.write("%3i  %s\n" % (id, self[id]))
        output.close()

def assignNullRois(roiIds):
    """Ensure every source in the POINTSOURCES table has an ROI_ID if it
    is in a source region."""
    sql = "select PTSRC_NAME, ra, dec from POINTSOURCES where ROI_ID IS NULL"
    srcs = dbAccess.apply(sql, lambda curs : [entry[:3] for entry in curs])
    for src in srcs:
        id = roiIds(src[1], src[2])
        if id is not None:
            sql = ("update POINTSOURCES set ROI_ID=%i where PTSRC_NAME='%s'" 
                   % (id, src[0]))
            dbAccess.apply(sql)

if __name__ == '__main__':
    import os
    from read_data import read_data
    from readXml import SourceModel
    from crearoi import crearoi
    import pipeline

    os.chdir(os.environ['OUTPUTDIR'])

    #
    # Read in the predefined ROIS from the db table
    #
    roiIds = RoiIds()

    #
    # Loop through the point sources and find those which do not
    # have a valid ROI.
    #
    ptsrcs = SourceModel('point_sources.xml')
    srcNames = ptsrcs.names()
    srcNames.sort()
    print "total number of sources:", len(srcNames)

    ids, ras, decs = [], [], []

    for id, srcName in enumerate(srcNames):
        ra, dec = (ptsrcs[srcName].spatialModel.RA.value,
                   ptsrcs[srcName].spatialModel.DEC.value)
        if roiIds(ra, dec) is None:
            ids.append(id)
            ras.append(ra)
            decs.append(dec)
            print srcName, id, ra, dec

    roiIds.write('predefined_rois.txt')
    crearoi(ids, ras, decs, 20, 'new_rois.txt',roi_id_offset=max(roiIds.keys()))

    os.system('cat predefined_rois.txt new_rois.txt > rois.txt')

    os.chmod('rois.txt', 0666)

    rois = read_data('rois.txt')
    nrois = len(rois[0])
    roi_ids = ("%i "*nrois) % tuple(rois[0])
    pipeline.setVariable('ROI_IDS', roi_ids)

