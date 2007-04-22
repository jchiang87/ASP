"""
@brief Interface to manage the list of Data Release Plan sources.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import celgal

class DrpSource(object):
    def __init__(self, name, ra, dec):
        self.name = name
        self.radec = ra, dec
    def dist(self, radec):
        return celgal.dist(self.radec, radec)

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

drpSources = DrpSources(os.path.join(os.environ['PYASPROOT'], 'data',
                                     'DRP_SourceList.txt'))
