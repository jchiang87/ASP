"""
@brief Implementation of Jay and Jerry's clustering algorithm based on
a user-selectable acceptance cone.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num
from pyIrfLoader import SkyDir

_eventId = 0
class Event(object):
    """Encapsulation of a LAT photon event in terms of apparent direction,
    arrival time, apparent energy, and event class.
    """
    def __init__(self, ra, dec, time, energy, evt_class):
        self.dir = SkyDir(ra, dec)
        self.ra, self.dec, self.energy = ra, dec, energy
        self.evt_class = evt_class
        self.time = time
        global _eventId
        self.id = _eventId
        _eventId += 1
    def sep(self, event):
        "Separation in degrees from another Event"
        return self.dir.difference(event.dir)*180./num.pi
    def __eq__(self, other):
        return self.id == other.id
    def __ne__(self, other):
        return not self==other
    def __repr__(self):
        #return '%.3f %.3f %.3f' % (self.ra, self.dec, self.time)
        return `self.id`

def convert(events, imin=0, imax=None):
    """Used by BlindSearch to convert a FitsNTuple of an FT1 file(s)
    to a list of Event objects over a range if indices, generally
    indicating a time range.
    """
    if imax is None:
        imax = len(events.RA)
    my_events = []
    for evt_tuple in zip(events.RA[imin:imax], events.DEC[imin:imax],
                         events.TIME[imin:imax], events.ENERGY[imin:imax],
                         events.EVENT_CLASS[imin:imax]):
        my_events.append(Event(*evt_tuple))
    return my_events

class EventClusters(object):
    "Jay Norris and Jerry Bonnell's photon clustering algorithm."
    def __init__(self, events):
        "events is a list of Event objects"
        dists = {}
        for evt in events:
            dists[evt] = []
            for other in events:
                dists[evt].append(evt.sep(other))
            dists[evt] = num.array(dists[evt])
        self.dists = dists
    def _clusterSizes(self, radius=10):
        sizes = {}
        for evt in self.dists:
            sizes[evt] = len(num.where(self.dists[evt] < radius)[0])
        return sizes
    def _findCluster(self, event, radius):
        cluster = []
        for evt in self.dists:
            if evt.sep(event) < radius:
                cluster.append(evt)
        return cluster
    def _largestCluster(self, radius):
        sizes = self._clusterSizes(radius)
        maxnum = 0
        for evt in sizes:
            if maxnum < sizes[evt]:
                largest = evt
                maxnum = sizes[evt]
        return self._findCluster(largest, radius)
    def _meanDir(self, cluster):
        ra = 0
        dec = 0
        for event in cluster:
            ra += event.ra
            dec += event.dec
        return SkyDir(ra/len(cluster), dec/len(cluster))
    def _cluster_dists(self, cluster):
        """Cluster distances from mean direction in radians"""
        mDir = self._meanDir(cluster)
        dists = []
        for item in cluster:
            dists.append(item.dir.difference(mDir))
        return num.array(dists)
    def logLike(self, radius=17, bg_rate=None):
        """Compute the log-likelihood that the stored events are
        *not* clustered in time or position, i.e., the log-likelihood of
        the null hypothesis.
        """
        times = []
        for evt in self.dists:
            times.append(evt.time)
        times.sort()
        times = num.array(times)
        dts = times[1:] - times[:-1]
        if bg_rate is None:
            bg_rate = len(times)/(times[-1] - times[0])
        xvals = bg_rate*dts
        logPdts = sum(num.log(1. - num.exp(-xvals)))

        max_cluster = self._largestCluster(radius)
        if len(max_cluster) < 2:
            raise ValueError, 'Largest cluster size < 2'
        dists = self._cluster_dists(max_cluster)
        logPdists = sum(num.log(1. - num.cos(dists)))

        return logPdts, logPdists
    def localize(self, cluster=None, radius=5):
        """Return the cluster (or largest, most significant cluster by 
        default) mean direction as a SkyDir object along with the
        (ra, dec) values of each event in the cluster.
        """
        if cluster is None:
            cluster = self._largestCluster(radius)
        ras, decs = [], []
        for event in cluster:
            ras.append(event.ra)
            decs.append(event.dec)
        return self._meanDir(cluster), ras, decs
