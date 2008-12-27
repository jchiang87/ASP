"""
@file drpDbAccess.py
@brief Functions to access the SourceMonitoring database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import sys
from databaseAccess import apply, cx_Oracle, getDbObjects, asp_default
import databaseAccess as dbAccess
import numarray as num
from xml.dom import minidom
from cleanXml import cleanXml

def dircos(ra, dec):
    nx = num.cos(dec*num.pi/180.)*num.cos(ra*num.pi/180.)
    ny = num.cos(dec*num.pi/180.)*num.sin(ra*num.pi/180.)
    nz = num.sin(dec*num.pi/180.)
    return num.array((nx, ny, nz))

def insertRoi(id, ra, dec, radius, sr_rad):
    sql = ("insert into ROIS (ROI_ID, RA, DEC, RADIUS, SR_RADIUS, 0) "
           + "values (%i, %.3f, %.3f, %i, %i)" % (id, ra, dec, radius, sr_rad))
    apply(sql)

def updateRoi(id, **kwds):
    sql_template = ("update ROIS set %s = %s where ROI = %i"
                    % ('%s', '%s', id))
    for key in kwds:
        sql = sql_template % (key, kwds[key])
        apply(sql)

def readRois(outfile='rois.txt'):
    output = open(outfile, 'w')
    sql = "select ROI_ID, RA, DEC, RADIUS, SR_RADIUS from ROIS where group_id=0 order by ROI_ID ASC"
    def cursorFunc(cursor):
        for entry in cursor:
            pars = tuple([x for x in entry])
            output.write("%i  %7.3f  %7.3f  %i  %i\n" % pars)
        output.close()
    return apply(sql, cursorFunc)

def inspectRois():
    rois = getDbObjects('ROIS')
# repackage by primary key
    roi_data = {}
    for roi in rois:
        roi_data[roi['ROI_ID']] = roi
    for id in roi_data:
        ra, dec = roi_data[id]['RA'], roi_data[id]['DEC']
        nhat = dircos(ra, dec)
        ptsrcs = findPointSources(ra, dec, roi_data[id]['RADIUS'])
        sys.stdout.write("ROI_ID %i:\n" % id)
        for ptsrc in ptsrcs:
            src = ptsrcs[ptsrc]
            sys.stdout.write("   %-30s  %.3f  %.3f  %.3e\n" %
                             (ptsrc, src.ra, src.dec,
                              num.arccos(src.cos_sep(nhat))*180./num.pi))

def defaultPtSrcXml(name, ra, dec):
    xml_template = """<source name="%s" type="PointSource">
  <spectrum type="PowerLaw2">
    <parameter free="1" max="1000.0" min="1e-05" name="Integral" scale="1e-06" value="1"/>
    <parameter free="1" max="-1.5" min="-5.0" name="Index" scale="1.0" value="-2"/>
    <parameter free="0" max="200000.0" min="20.0" name="LowerLimit" scale="1.0" value="20.0"/>
    <parameter free="0" max="200000.0" min="20.0" name="UpperLimit" scale="1.0" value="200000.0"/>
  </spectrum>
  <spatialModel type="SkyDirFunction">
    <parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="%.3f"/>
    <parameter free="0" max="90.0" min="-90.0" name="DEC" scale="1.0" value="%.3f"/>
  </spatialModel>
</source>
"""
    return xml_template % (name, ra, dec)

class PointSource(object):
    def __init__(self, entry, roiIds=None):
        self.name = entry[0]
        self.ra = entry[2]
        self.dec = entry[3]
        self.nhat = entry[4:7]
        if roiIds is not None:
            self.roi_id = roiIds(self.ra, self.dec)
        else:
            self.roi_id = entry[1]
        try:
            self.xml = entry[7].read()
        except AttributeError:
            # This entry has no xml definition, so use default
            self.xml = defaultPtSrcXml(self.name, self.ra, self.dec)
    def domElement(self):
        return minidom.parseString(self.xml).getElementsByTagName('source')[0]
    def cos_sep(self, nhat):
        return sum(nhat*self.nhat)
    def __repr__(self):
        return "%s  %.3f  %.3f" % (self.name, self.ra, self.dec)

class PointSourceDict(dict):
    def __init__(self):
        dict.__init__(self)
    def select(self, roi_id):
        my_sources = []
        for source in self.keys():
            if self[source].roi_id == roi_id:
                my_sources.append(source)
        return my_sources

def findPointSources(ra, dec, radius, srctype=None, roiIds=None,
                     connection=asp_default):
    nhat = dircos(ra, dec)
    mincos = num.cos(radius*num.pi/180.)
    sql = """select pointsources.ptsrc_name, pointsources.roi_id,
             pointsources.ra, pointsources.dec,
             pointsources.nx, pointsources.ny, pointsources.nz,
             pointsources.xml_model
             from PointSources
             left join pointsourcetypeset on (pointsources.ptsrc_name =
             pointsourcetypeset.ptsrc_name)"""
    if srctype:
        sql += " where pointsourcetypeset.SOURCESUB_TYPE = '%s'" % srctype
    def getSources(cursor):
        srcs = PointSourceDict()
        for entry in cursor:
            src = PointSource(entry, roiIds=roiIds)
            if src.cos_sep(nhat) > mincos:
                srcs[entry[0]] = src
        return srcs
    return apply(sql, getSources, connection=connection)

def findUniquePointSources(ra, dec, radius, roiIds=None, tol=0.5,
                           connection=asp_default):
    """Screen by SOURCE_TYPE, giving precedence to known sources
    (e.g., DRP, Blazar, Pulsar) over tentative IDs from pgwave that may
    duplicate these known sources.    
    """
    nhat = dircos(ra, dec)
    mincos = num.cos(radius*num.pi/180.)
    sql = """select pointsources.ptsrc_name, pointsources.roi_id,
             pointsources.ra, pointsources.dec,
             pointsources.nx, pointsources.ny, pointsources.nz,
             pointsources.xml_model,
             pointsourcetypeset.sourcesub_type from PointSources
             left join pointsourcetypeset on (pointsources.ptsrc_name =
             pointsourcetypeset.ptsrc_name)
             where pointsourcetypeset.sourcesub_type = 'DRP' or
             pointsourcetypeset.sourcesub_type = 'BLZRGRPSRC' or
             pointsourcetypeset.sourcesub_type = 'KNOWNPSR' or
             pointsourcetypeset.sourcesub_type = 'PGWAVE' or
             pointsourcetypeset.sourcesub_type = 'ATEL'"""
    def getSources(cursor):
        srcs = PointSourceDict()
        for entry in cursor:
            src = PointSource(entry, roiIds=roiIds)
            src.sourceType = entry[-1]
            if src.cos_sep(nhat) > mincos:
                srcs[entry[0]] = src
        return srcs
    my_dict = apply(sql, getSources, connection=connection)

    known_list = [srcName for srcName in my_dict 
                  if my_dict[srcName].sourceType in ('DRP', 'BLZRGRPSRC', 
                                                     'KNOWNPSR')]

    ok_pgwave_sources = []
    cos_tol = num.cos(tol*num.pi/180.)
    for srcName in my_dict:
       if (my_dict[srcName].sourceType == 'PGWAVE' or
           my_dict[srcName].sourceType == 'ATEL'):
            addSource = True
            for knownSource in known_list:
                nhat = num.array(my_dict[knownSource].nhat)
                cos_sep = my_dict[srcName].cos_sep(nhat)
                if cos_sep > cos_tol:
                    addSource = False
                    print srcName, cos_sep
                    continue
            if addSource:
                ok_pgwave_sources.append(srcName)
    
    known_list.extend(ok_pgwave_sources)
    uniq_dict = PointSourceDict()
    for item in known_list:
        uniq_dict[item] = my_dict[item]

    return uniq_dict

class DiffuseSource(object):
    def __init__(self, entry):
        self.xml = entry[1].read()
    def domElement(self):
        return minidom.parseString(self.xml).getElementsByTagName('source')[0]

def findDiffuseSources():
    "Read the xml model from the db tables for Diffuse Sources"
    sql = "select * from DIFFUSESOURCES"
    def cursorFunc(cursor):
        srcs = {}
        for entry in cursor:
            if entry[2] == 0:
                srcs[entry[0]] = DiffuseSource(entry)
        return srcs
    return apply(sql, cursorFunc)

def buildXmlModel(ra, dec, radius, outfile):
    ptsrcs = findPointSources(ra, dec, radius)
    diffuse = findDiffuseSources()
    xmlModel = """<?xml version="1.0" ?>
<source_library title="Likelihood model">
</source_library>
"""
    doc = minidom.parseString(xmlModel)
    lib = doc.getElementsByTagName('source_library')[0]
    for src in ptsrcs:
        lib.appendChild(ptsrcs[src].domElement())
    for src in diffuse:
        lib.appendChild(diffuse[src].domElement())
    xmlModel = cleanXml(doc)
    output = open(outfile, 'w')
    output.write(xmlModel.toxml() + "\n")
    output.close()

if __name__ == "__main__":
#    from read_data import read_data
#    for items in zip(*read_data('rois_gino.txt')):
#        id = items[0]
#        sr_radius = items[-1]
#        updateRoi(id, SR_RADIUS=sr_radius)
    buildXmlModel(193.98, -5.82, 20, 'my_model.xml')
