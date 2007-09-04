"""
@file drpDbAccess.py
@brief Functions to access the SourceMonitoring database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
from databaseAccess import apply, cx_Oracle
import numarray as num
from xml.dom import minidom
from cleanXml import cleanXml

def dircos(ra, dec):
    nx = num.cos(dec*num.pi/180.)*num.cos(ra*num.pi/180.)
    ny = num.cos(dec*num.pi/180.)*num.sin(ra*num.pi/180.)
    nz = num.sin(dec*num.pi/180.)
    return num.array((nx, ny, nz))

def insertRoi(id, ra, dec, radius):
    sql = ("insert into SOURCEMONITORINGROI (ROI, RA, DEC, RADIUS) "
           + "values (%i, %.3f, %.3f, %i)" % (id, ra, dec, radius))
    apply(sql)

def findRois(ra_val, dec_val):
    nhat = dircos(ra_val, dec_val)
    sql = "select * from SOURCEMONITORINGROI"
    def cursorFunc(cursor):
        rois = {}
        for entry in cursor:
            id, ra, dec, radius = [x for x in entry]
            roi_nhat = dircos(ra, dec)
            mu = sum(roi_nhat*nhat)
            if mu > num.cos(radius*num.pi/180.):
                rois[id] = num.arccos(mu)*180./num.pi
        return rois
    return apply(sql, cursorFunc)

def findPointSources(ra, dec, radius, srctype=None):
    nhat = dircos(ra, dec)
    mincos = num.cos(radius*num.pi/180.)
    sql = "select * from SOURCEMONITORINGPOINTSOURCE"
    if srctype:
        sql += " where SOURCETYPE = %s" % srctype
    def cursorFunc(cursor):
        srcs = {}
        for entry in cursor:
            src_nhat = num.array(entry[4:7])
            if sum(src_nhat*nhat) > mincos:
                srcs[entry[0]] = entry[2], entry[3]
        return srcs
    return apply(sql, cursorFunc)

def findDiffuseSources():
    sql = "select * from SOURCEMONITORINGDIFFUSESOURCE"
    def cursorFunc(cursor):
        srcs = {}
        for entry in cursor:
            srcs[entry[0]] = entry[1]
        return srcs
    return apply(sql, cursorFunc)

def buildXmlModel(ra, dec, radius, outfile):
    ptsrcs = findPointSources(ra, dec, radius)
    diffuse = findDiffuseSources()
    sourceNames = ptsrcs.keys()
    sourceNames.extend(diffuse.keys())
    sql = "select * from SOURCEMONITORINGSOURCE"
    def cursorFunc(cursor):
        xmlModel = """<?xml version="1.0" ?>
<source_library title="Likelihood model">
</source_library>
"""
        doc = minidom.parseString(xmlModel)
        lib = doc.getElementsByTagName('source_library')[0]
        for entry in cursor:
            if entry[0] in sourceNames:
                xmldef = entry[3].read()
                source = minidom.parseString(xmldef).getElementsByTagName('source')[0]
                lib.appendChild(source)
        return doc
    xmlModel = apply(sql, cursorFunc)
    xmlModel = cleanXml(xmlModel)
    output = open(outfile, 'w')
    output.write(xmlModel.toxml() + "\n")
    output.close()

if __name__ == "__main__":
#    from read_data import read_data
#    for items in zip(*read_data('rois_gino.txt')):
#        insertRoi(*items[:-1])
    print findRois(193.98, -5.82)
    buildXmlModel(193.98, -5.82, 20, 'my_model.xml')

