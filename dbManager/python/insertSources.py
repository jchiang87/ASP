import readXml
import databaseAccess as dbAccess
from AspHealPix import Healpix, SkyDir
from celgal import dist
from drpDbAccess import dircos

_hp = Healpix(32)

def hp_id(ra, dec):
    return _hp.coord2pix(SkyDir(ra, dec))

class Roi(object):
    def __init__(self, roi_dict):
        self.__dict__.update(roi_dict)
    def sep(self, ra, dec):
        return dist((self.RA, self.DEC), (ra, dec))

class Rois(list):
    def __init__(self):
        list.__init__(self)
        rois = dbAccess.getDbObjects('ROIS')
        for item in rois:
            self.append(Roi(item))

_rois = Rois()

def roi_id(ra, dec):
    "Compute the roi with center closest to the specified location."
    minsep = _rois[0].sep(ra, dec)
    my_roi = _rois[0].ROI_ID
    for roi in _rois[1:]:
        sep = roi.sep(ra, dec)
        if sep < minsep:
            minsep = sep
            my_roi = roi.ROI_ID
    return my_roi

srcModel = readXml.SourceModel('AspSrcModel.xml')

for name in srcModel.names():
    src = srcModel[name]
    xmldef = src.node.toxml().encode()
    if src.type == 'PointSource':
        ra, dec = src.spatialModel.RA.value, src.spatialModel.DEC.value
        hpId = hp_id(ra, dec)
        roiId = roi_id(ra, dec)
        srcType = src.sourceType
        specType = src.spectrum.type
        nhat = dircos(ra, dec)
        if srcType == 'DRP':
            ispublic = 1
        else:
            ispublic = 0
        sql = ("insert into POINTSOURCES (PTSRC_NAME, HEALPIX_ID, ROI_ID, "
               + "SOURCE_TYPE, SPECTRUM_TYPE, RA, DEC, ERROR_RADIUS, "
               + "POSITION_QUALITY, NX, NY, NZ, XML_MODEL, IS_OBSOLETE, "
               + "IS_PUBLIC) values ('%s', %i, %i, '%s', '%s', %f, %f, %f, "
               + "%f, %f, %f, %f, '%s', '%i', '%i')")
        sql = sql % (name, hpId, roiId, srcType, specType, ra, dec, 0, -1,
                     nhat[0], nhat[1], nhat[2], xmldef, 0, ispublic)
    else:
        sql = ("insert into DIFFUSESOURCES " +
               "(DIFFSRC_NAME, XML_MODEL, IS_OBSOLETE) " +
               "values ('%s', '%s', '%i')")
        sql = sql % (name, xmldef, 0)
    dbAccess.apply(sql)
