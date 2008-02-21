"""
@brief Use PSF to determine cluster locations and to construct spatial
part of log-likelihood.

@author J. Chiang <jchiang@sla.stanford.edu>
"""
#
# $Header$
#

import numpy as num
import pyIrfLoader
from ScData import ScData
SkyDir = pyIrfLoader.SkyDir

_scData = ScData()

pyIrfLoader.Loader_go()
_irfsFactory = pyIrfLoader.IrfsFactory_instance()

irfs = ('DC2::FrontA', 'DC2::BackA', 'DC2::FrontB', 'DC2::BackB')
#irfs = ('DC1A::Front', 'DC1A::Back', 'DC1A::Front', 'DC1A::Back')
_psfs = [_irfsFactory.create(irf).psf() for irf in irfs]

class PsfClusters(object):
    def __init__(self, events):
        dists = {}
        for evt in events:
            dists[evt] = []
            for other in events:
                dists[evt].append( (evt.sep(other), other) )
        self.dists = dists
    def _clusterSizes(self):
        sizes = {}
        for evt in self.dists:
            sizes[evt] = self._psfLogLike(evt)
        return sizes
    def _psfLogLike(self, evt):
        logLike = 0
        psf_wts = {}
        theta = _scData.inclination(evt.time, evt.dir)
        for sep, other in self.dists[evt]:
            psf = _psfs[evt.evt_class]
            psf_wts[other] = psf.value(sep, other.energy, theta, 0)
            logLike += num.log(psf_wts[other])
        return logLike, psf_wts
    def _largestCluster(self, radius=None):
        sizes = self._clusterSizes()
        maxval = sizes[sizes.keys()[0]]
        for evt in sizes:
            if maxval[0] < sizes[evt][0]:
                largest = evt
                maxval = sizes[evt]
        return maxval
    def logLike(self, radius=None, bg_rate=None):
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

        max_cluster = self._largestCluster()
        logPdists = -max_cluster[0]
        
        return logPdts, logPdists
    def localize(self, cluster=None):
        if cluster is None:
            logLike, psf_wts = self._largestCluster()
        ra_avg, dec_avg, norm = 0, 0, 0
        ras, decs = [], []
        for evt in psf_wts:
            ras.append(evt.ra)
            decs.append(evt.dec)
            ra_avg += evt.ra*psf_wts[evt]
            dec_avg += evt.dec*psf_wts[evt]
            norm += psf_wts[evt]
        return SkyDir(ra_avg/norm, dec_avg/norm), ras, decs

if __name__ == '__main__':
    import os
    from FitsNTuple import FitsNTuple
    import hippoplotter as plot
    from blind_search import BlindSearch
    
    downlink = os.environ['DOWNLINKFILE']
    events = FitsNTuple(downlink)
    blindSearch = BlindSearch(events, clusterAlg=PsfClusters)
    
    plot.scatter(blindSearch.times, blindSearch.logdts, pointRep='Line')
    plot.scatter(blindSearch.times, blindSearch.logdists, pointRep='Line')
    logLike = blindSearch.logdts + blindSearch.logdists
    plot.scatter(blindSearch.times, logLike, pointRep='Line')

    hist = plot.histogram(events.TIME)
    hist.setBinWidth('x', 5)

    grb_dirs = blindSearch.grbDirs()
    for grb in grb_dirs:
        plot.xyhist(grb[1], grb[2], xname='RA', yname='Dec')
        plot.vline(grb[0].ra())
        plot.hline(grb[0].dec())
