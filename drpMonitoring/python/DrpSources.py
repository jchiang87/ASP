"""
@brief Interface to manage the list of Data Release Plan sources.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from xml.dom import minidom
import celgal

class MonitoredSource(object):
    def __init__(self, node):
        self.name = node.getAttribute('name').encode()
        self.radec = self._getCoords(node)
    def _getCoords(self, node):
        pars = node.getElementsByTagName('parameter')
        for item in pars:
            if item.getAttribute('name') == 'RA':
                ra = float(item.getAttribute('value'))
            if item.getAttribute('name') == 'DEC':
                dec = float(item.getAttribute('value'))
        return ra, dec
    def dist(self, radec):
        return celgal.dist(self.radec, radec)

class MonitoredSources(dict):
    def __init__(self, xmlFile):
        dict.__init__(self)
        foo = minidom.parse(xmlFile)
        doc = foo.getElementsByTagName('source_library')[0]
        srcs = doc.getElementsByTagName('source')
        for item in srcs:
            name = item.getAttribute('name').encode()
            self[name] = MonitoredSource(item)
    def select(self, ra, dec, radius):
        my_sources = []
        for source in self.keys():
            if self[source].dist((ra, dec)) < radius:
                my_sources.append(source)
        return my_sources

class DrpSource(object):
    def __init__(self, name, ra, dec):
        self.name = name
        self.radec = ra, dec
    def dist(self, radec):
        return celgal.dist(self.radec, radec)
    def __repr__(self):
        return "%s  %.3f  %.3f" % (self.name, self.radec[0], self.radec[1])

class DrpSources(dict):
    def __init__(self, infile):
        dict.__init__(self)
        for line in open(infile):
            if line.find("#") != 0:
                name, coord = line[1:].split('"')
                ra, dec = coord.strip().split()
                ra, dec = float(ra), float(dec)
                self[name] = DrpSource(name, ra, dec)
    def select(self, ra, dec, radius):
        my_sources = []
        for source in self.keys():
            if self[source].dist((ra, dec)) < radius:
                my_sources.append(source)
        return my_sources

drpSources = DrpSources(os.path.join(os.environ['DRPMONITORINGROOT'], 'data',
                                     'DRP_SourceList.txt'))
blazars = MonitoredSources(os.path.join(os.environ['DRPMONITORINGROOT'], 'data',
                                        'BM_only.xml'))
