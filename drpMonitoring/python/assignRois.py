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
from parfile_parser import Parfile
import pyfits

from GtApp import GtApp
gtselect = GtApp('gtselect')
gtmktime = GtApp('gtmktime')

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
            sql = "select ROI_ID, RA, DEC, RADIUS, SR_RADIUS from ROIS where group_id=0"
            def readRoiTable(cursor):
                for item in cursor:
                    self[item[0]] = Roi(*item[1:])
            dbAccess.apply(sql, readRoiTable)
        else:
            data = read_data(infile)
            for line in zip(*data):
                self[line[0]] = Roi(*line[1:])
    def __call__(self, ra, dec, offset=0):
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

def testRois(infile='rois.txt'):
    """Perform the initial acceptance cone selection and GTI generation
    and filtering for each roi.  Return a tuple of non-null
    selections.
    """
    pars = Parfile('drp_pars.txt')
    roi_ok = []
    for id, ra, dec, rad, src_rad in zip(*read_data(infile)):
        gtselect.run(infile=pars['ft1file'], outfile='ft1_events_no_zen.fits',
                     ra=ra, dec=dec, rad=rad, emin=30, emax=3e5,
                     tmin=pars['start_time'], tmax=pars['stop_time'])
        gtmktime['evfile'] = gtselect['outfile']
        gtmktime['outfile'] = 'ft1_events.fits'
        gtmktime['scfile'] = pars['ft2file']
        gtmktime['roicut'] = 'yes'
        gtmktime['filter'] = 'LIVETIME>0'
        try:
            gtmktime.run()
        except RuntimeError:
            filter = "angsep(RA_ZENITH,DEC_ZENITH,RA_SCZ,DEC_SCZ)<47 || angsep(RA_ZENITH,DEC_ZENITH,%.3f,%.3f)<%.3f" % (ra, dec, pars['zenmax']-rad)
            try:
                gtmktime.run(filter=filter, roicut='no')
            except:
                continue
        ft1 = pyfits.open(gtmktime['outfile'])
        if ft1['EVENTS'].header['NAXIS2'] > 0:
            roi_ok.append(id)
        #
        # clean up
        #
        os.remove(gtselect['outfile'])
        os.remove(gtmktime['outfile'])
    return roi_ok

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

#    rois = read_data('rois.txt')
#    nrois = len(rois[0])
#    roi_ids = ("%i "*nrois) % tuple(rois[0])
#    pipeline.setVariable('ROI_IDS', roi_ids)

    rois = testRois('rois.txt')
    nrois = len(rois)
    roi_ids = ("%i "*nrois) % tuple(rois)
    pipeline.setVariable('ROI_IDS', roi_ids)
