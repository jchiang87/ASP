"""
@brief Script to replace catalog sources with DRP source names and
positions, adding sources as necessary.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

from xml.dom import minidom
from celgal import dist

_ptsrc_template = """
<source name="%s" type="PointSource">
    <spectrum type="PowerLaw2">
      <parameter free="1" max="1000.0" min="1e-05" name="Integral" scale="1e-06" value="1.159"/>
      <parameter free="1" max="0.0" min="-5.0" name="Index" scale="1.0" value="-2.35"/>
      <parameter free="0" max="200000.0" min="20.0" name="LowerLimit" scale="1.0" value="20.0"/>
      <parameter free="0" max="200000.0" min="20.0" name="UpperLimit" scale="1.0" value="200000.0"/>
    </spectrum>
    <spatialModel type="SkyDirFunction">
      <parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="%.3f"/>
      <parameter free="0" max="90.0" min="-90.0" name="DEC" scale="1.0" value="%.3f"/>
    </spatialModel>
  </source>
"""

def newSrc(name, ra, dec):
    foo = minidom.parseString(_ptsrc_template % (name, ra, dec))
    return foo.getElementsByTagName("source")[0]

def read_source_list(infile="DRP_SourceList.txt"):
    my_dict = {}
    for line in open(infile):
        if line.find("#") != 0:
            name, coord = line[1:].split('"')
            ra, dec = coord.strip().split()
            ra, dec = float(ra), float(dec)
            my_dict[name] = (ra, dec)
    return my_dict

class Source(object):
    def __init__(self, src):
        self.name = src.getAttribute("name")
        self.src = src

class PointSource(Source):
    def __init__(self, src):
        Source.__init__(self, src)
        self._readCoords()
    def _readCoords(self):
        pars = self._getPositionPars()
        for par in pars:
            if par.getAttribute("name") == "RA":
                ra = float(par.getAttribute("value"))
            if par.getAttribute("name") == "DEC":
                dec = float(par.getAttribute("value"))
        self.coords = ra, dec
    def _getPositionPars(self):
        pos = self.src.getElementsByTagName("spatialModel")[0]
        return pos.getElementsByTagName("parameter")
    def dist(self, coords):
        return dist(self.coords, coords)
    def setCoords(self, ra, dec):
        pars = self._getPositionPars()
        for par in pars:
            if par.getAttribute("name") == "RA":
                par.setAttribute("value", "%.3f" % ra)
            if par.getAttribute("name") == "DEC":
                par.setAttribute("value", "%.3f" % dec)
        self._readCoords()
    def setName(self, name):
        self.src.setAttribute("name", name)
        self.name = name

def read_xml(infile='LATSourceCatalog_v2.xml'):
    doc = minidom.parse(infile)
    srcs = doc.getElementsByTagName('source')
    ptsrcs = []
    diffuse = []
    for src in srcs:
        if src.getAttribute("type") == "PointSource":
            ptsrcs.append(PointSource(src))
        else:
            diffuse.append(Source(src))
    return doc, ptsrcs, diffuse

if __name__ == '__main__':
    drpSources = read_source_list()
    doc, ptsrcs, diffuse = read_xml()

    tol = 0.5
    newSrcs = []
    for src in drpSources:
        print src, ": "
        count = 0
        for ptsrc in ptsrcs:
            sep = ptsrc.dist(drpSources[src])
            if sep < tol and count < 1:
                print "   ", ptsrc.name
                ptsrc.setName(src)
                ptsrc.setCoords(*drpSources[src])
                count += 1
        if count == 0:
            newSrcs.append(newSrc(src, *drpSources[src]))

    for item in newSrcs:
        doc.getElementsByTagName("source_library")[0].appendChild(item)

    output = open('DRP_SourceModel.xml', 'w')
    output.write(doc.toxml() + "\n")
    output.close()
    
