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
from GtApp import GtApp
from readXml import SourceModel, Source
from cleanXml import cleanXml
from drpDbAccess import apply, findPointSources
from celgal import celgal, dist

converter = celgal()

os.chdir(os.environ['OUTPUTDIR'])

gtbin = GtApp('gtbin')
gtbin['evfile'] = 'time_filtered_events.fits'
gtbin['outfile'] = 'cmap.fits'
gtbin['algorithm'] = 'CMAP'
gtbin.run(nxpix=720, nypix=360, binsz=0.5, coordsys='GAL',
          xref=0, yref=0, axisrot=0, proj='CAR')

pgwave = GtApp('pgwave2D', 'pgwave')
pgwave['input_file'] = gtbin['outfile']
pgwave['bgk_choise'] = "n"
pgwave['circ_square'] = "s"
pgwave.run(kappa=5)

_xml_template = """<source name="%s" type="PointSource">
  <spectrum type="PowerLaw2">
    <parameter free="1" max="1000.0" min="1e-05" name="Integral" scale="1e-06" value="1"/>
    <parameter free="1" max="0.0" min="-5.0" name="Index" scale="1.0" value="-2"/>
    <parameter free="0" max="200000.0" min="20.0" name="LowerLimit" scale="1.0" value="20.0"/>
    <parameter free="0" max="200000.0" min="20.0" name="UpperLimit" scale="1.0" value="200000.0"/>
  </spectrum>
  <spatialModel type="SkyDirFunction">
    <parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="%.3f"/>
    <parameter free="0" max="90.0" min="-90.0" name="DEC" scale="1.0" value="%.3f"/>
  </spatialModel>
</source>
"""

ptsrcs = findPointSources(0, 0, 180)

sql = "select * from SOURCEMONITORINGSOURCE"
def cursorFunc(cursor):
    xmlModel = """<?xml version="1.0" ?>
<source_library title="Likelihood model">
</source_library>
"""
    doc = minidom.parseString(xmlModel)
    lib = doc.getElementsByTagName('source_library')[0]
    for entry in cursor:
        if (entry[0] in ptsrcs.keys() and entry[0].find('l b') != 0
            and entry[0].find('_3EG') !=0):
            xmldef = entry[3].read()
            source = minidom.parseString(xmldef).getElementsByTagName('source')[0]
            lib.appendChild(source)
    return doc
xmlModel = apply(sql, cursorFunc)
xmlModel = cleanXml(xmlModel)

outfile = "point_sources.xml"
output = open(outfile, 'w')
output.write(xmlModel.toxml() + "\n")
output.close()

foo = SourceModel(outfile)

class PgwaveSource(object):
    def __init__(self, line):
        data = line.split()
        self.id = int(data[0])
        self.l, self.b = float(data[3]), float(data[4])
        self.ra, self.dec = converter.cel((self.l, self.b))
        self.snr = float(data[5])
    def dist(self, xmlsrc):
        ra = xmlsrc.spatialModel.RA.value
        dec = xmlsrc.spatialModel.DEC.value
        return dist((self.ra, self.dec), (ra, dec))

pg_srcs = [PgwaveSource(line) for line in open('cmap.list') if line.find("#")==-1]

for src in pg_srcs:
    add = True
    for item in foo.names():
        if src.dist(foo[item]) < 0.5:
            add = False
    if add:
        name = "pgw_%04i" % src.id
        xmldef = minidom.parseString(_xml_template % (name, src.ra, src.dec)).getElementsByTagName('source')[0]
        foo[name] = Source(xmldef)

foo.writeTo('point_sources.xml')
