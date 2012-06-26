from xml.dom import minidom
from celgal import dist

def read_source_list(infile="DRP_SourceList.txt"):
    my_dict = {}
    for line in open(infile):
        if line.find("#") != 0:
            name, coord = line[1:].split('"')
            ra, dec = coord.strip().split()
            ra, dec = float(ra), float(dec)
            my_dict[name] = (ra, dec)
    return my_dict

class PointSource(object):
    def __init__(self, src):
        self.name = src.getAttribute("name").encode()
        pos = src.getElementsByTagName("spatialModel")[0]
        pars = pos.getElementsByTagName("parameter")
        for par in pars:
            if par.getAttribute("name") == "RA":
                ra = float(par.getAttribute("value"))
            if par.getAttribute("name") == "DEC":
                dec = float(par.getAttribute("value"))
        self.coords = (ra, dec)
    def dist(self, coords):
        return dist(self.coords, coords)

def read_xml(infile='LATSourceCatalog_v2.xml'):
    doc = minidom.parse(infile)
    srcs = doc.getElementsByTagName('source')
    ptsrcs = []
    for src in srcs:
        if src.getAttribute("type") == "PointSource":
            ptsrcs.append(PointSource(src))
    return ptsrcs

if __name__ == '__main__':
    drpSources = read_source_list()
    ptsrcs = read_xml()

    tol = 1
    for src in drpSources:
        print src, ": "
        for ptsrc in ptsrcs:
            sep = ptsrc.dist(drpSources[src])
            if sep < 0.5:
                print "  ", ptsrc.name, sep
