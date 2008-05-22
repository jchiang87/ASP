"""
@file MonitoredSources.py

@brief Provide a factory to create a dictionaries of sources that can
be selected by roi_id.  The sources are queried by SOURCE_TYPE from
the POINTSOURCES db table.

This factory and the objects it creates are kept separate from
drpDbAccess so that the creation overhead overhead is not incurred by
other scripts that need functions in drpDbAccess.py.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import drpDbAccess

class MonitoredSourceFactory(object):
    def __init__(self, srcTypes=('DRP', 'Blazar')):
        self.ptsrcs = {}
        for type in srcTypes:
            self.ptsrcs[type] = drpDbAccess.findPointSources(0, 0, 180, type)
    def create(self, srcType):
        sourceDict = drpDbAccess.PointSourceDict()
        for item in self.ptsrcs[srcType]:
            sourceDict[item] = self.ptsrcs[srcType][item]
        return sourceDict        

srcFactory = MonitoredSourceFactory()

drpSources = srcFactory.create('DRP')
blazars = srcFactory.create('Blazar')
