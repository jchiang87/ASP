"""
@file drpDbAccess.py
@brief Functions to access the SourceMonitoring database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import sys
from databaseAccess import apply, cx_Oracle, getDbObjects
import numarray as num
from xml.dom import minidom
from cleanXml import cleanXml

def dircos(ra, dec):
    nx = num.cos(dec*num.pi/180.)*num.cos(ra*num.pi/180.)
    ny = num.cos(dec*num.pi/180.)*num.sin(ra*num.pi/180.)
    nz = num.sin(dec*num.pi/180.)
    return num.array((nx, ny, nz))

def insertRoi(id, ra, dec, radius, sr_rad):
    sql = ("insert into ROIS (ROI_ID, RA, DEC, RADIUS, SR_RADIUS) "
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
    sql = "select * from ROIS"
    def cursorFunc(cursor):
        for entry in cursor:
            pars = tuple([x for x in entry])
            output.write("%i  %7.3f  %7.3f  %i  %i\n" % pars)
        output.close()
    return apply(sql, cursorFunc)

def findPointSources(ra, dec, radius, srctype=None):
    nhat = dircos(ra, dec)
    mincos = num.cos(radius*num.pi/180.)
    sql = "select * from POINTSOURCES"
    if srctype:
        sql += " where SOURCE_TYPE = '%s'" % srctype
    def cursorFunc(cursor):
        srcs = {}
        for entry in cursor:
            # Compute angular separation: get direction cosines
            src_nhat = num.array(entry[10:13])
            cos_sep = sum(src_nhat*nhat)
            if cos_sep > mincos:
                # fill with ra, dec, angular separation, and xml model
                srcs[entry[0]] = (entry[6], entry[7], num.arccos(cos_sep),
                                  entry[13].read())
        return srcs
    return apply(sql, cursorFunc)

def inspectRois():
    rois = getDbObjects('ROIS')
# repackage by primary key
    roi_data = {}
    for roi in rois:
        roi_data[roi['ROI_ID']] = roi
    for id in roi_data:
        ptsrcs = findPointSources(roi_data[id]['RA'], roi_data[id]['DEC'],
                                  roi_data[id]['RADIUS'])
        sys.stdout.write("ROI_ID %i:\n" % id)
        for ptsrc in ptsrcs:
            if ptsrc.find("HP") != 0:
                sys.stdout.write("   %-30s  %.3f  %.3f  %.3e\n" %
                                 (ptsrc, ptsrcs[ptsrc][0], ptsrcs[ptsrc][1],
                                  ptsrcs[ptsrc][2]))

def findDiffuseSources():
    "Read the xml model from the db tables for Diffuse Sources"
    sql = "select * from DIFFUSESOURCES"
    def cursorFunc(cursor):
        srcs = {}
        for entry in cursor:
            if entry[2] != "F" and entry[2] != "f":
                srcs[entry[0]] = entry[1].read()
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
        xmldef = ptsrcs[src][3]
        source = minidom.parseString(xmldef).getElementsByTagName('source')[0]
        lib.appendChild(source)
    for src in diffuse:
        xmldef = diffuse[src]
        source = minidom.parseString(xmldef).getElementsByTagName('source')[0]
        lib.appendChild(source)
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
