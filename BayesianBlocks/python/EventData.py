#!/usr/bin/env python
"""
Bayesian Blocks algorithm for time-tagged event data.  Based on the
algorithm described in Scargle et al. 2003 "Studies in Astronomical
Time Series Analysis. VI. Optimum Partition of the Interval: Bayesian
Blocks, Histograms, and Triggers" and Jackson et al. 200? "An
Algorithm for Optimal Partitioning of Data on an Interval"
"""
import copy
import math
import string
from gammaln import gammln

class EventData(object):
    eps = 1e-16
    def __init__(self, events):
        try:
            self._read(events)
        except:
            self.events = events
        self.events.sort()
        self._createCells()
    def __repr__(self):
        return `self.events`
    def cellSizes(self):
        cell_sizes = []
        for cell in self.cells:
            cell_sizes.append(cell[1] - cell[0])
        return cell_sizes
    def globalOpt(self, logGamma=1):
        opt = [self._blockCost(0, 0) - logGamma]
        last = [0]
        for nn in range(1, len(self.events)):
            results = [self._blockCost(0, nn) - logGamma]
            for jj in range(1, nn+1):
                results.append(opt[jj-1] + self._blockCost(jj, nn) - logGamma)
            opt.append(max(results))
            last.append(results.index(opt[-1]))
        change_points = []
        indx = last[-1]
        while indx > 0:
            change_points.insert(0, indx)
            indx = last[indx-1]
        return change_points, opt, last
    def lightCurve(self, changePoints):
        xx = []
        yy = []
        changePoints.insert(0, 0)
        changePoints.append(len(self.events) - 1)
        for i in xrange(1, len(changePoints)):
            imin = changePoints[i-1]
            imax = changePoints[i]
            dens = self._blockContent(imin, imax)/self._blockSize(imin, imax)
            xx.extend([self.cells[imin][0], self.cells[imax][0]])
            yy.extend([dens, dens])
        return (xx, yy)
    def writeTo(self, filename):
        file = open(filename, 'w')
        for event in self.events:
            file.write("%s\n" % event)
        file.close()
    def _read(self, filename):
        file = open(filename, 'r')
        self.events = []
        for line in file:
            self.events.append(string.atof(line)*1e3)
        file.close()
    def _createCells(self):
        events = self.events
        cell_boundaries = [(3.*events[0] - events[1])/2.]
        for i in xrange(1, len(events)):
            cell_boundaries.append((events[i-1] + events[i])/2.)
        cell_boundaries.append((3.*events[-1] - events[-2])/2.)
        self.cells = []
        for i in xrange(len(events)):
            self.cells.append((cell_boundaries[i], cell_boundaries[i+1]))
    def _blockCost(self, imin, imax):
        size = self._blockSize(imin, imax)
        content = self._blockContent(imin, imax)
        #arg = size - content + 1.;
        arg = size - content;
        if arg > 0:
            #my_cost = gammln(content + 1.) + gammln(arg) - gammln(size + 2.)
            my_cost = (gammln(content + 1.) + gammln(arg + 1.)
                       - gammln(size + 2.))
            return my_cost
        else:
            #return self.eps
            return -math.log(size)

    def _blockSize(self, imin, imax):
        return self.cells[imax][1] - self.cells[imin][0]
    def _blockContent(self, imin, imax):
        return imax - imin + 1.

if __name__ == '__main__':
    import sys
    import string, time
    import hippoplotter as plot
    from distributions import *

    plot.clear()
    
#    npts = 300
#    events = sample(stepFunction(0.3, 0.6), npts)
#    dt = []
#    for i in xrange(len(events)-1):
#        dt.append(abs(events[i+1] - events[i]))
#    events /= min(dt)/2.
    events = 'events.dat'
    evtData = EventData(events)
    hist = plot.histogram(evtData.events, 'event times', ylog=1)

    if len(sys.argv) == 2:
        logGamma = string.atof(sys.argv[1])
    else:
        logGamma = 1
    t0 = time.time()
    change_points, opt, last = evtData.globalOpt(logGamma)
    t1 = time.time()
    print t1-t0

    xx, yy = evtData.lightCurve(change_points)
    #plot.scatter(xx, yy, oplot=1, pointRep='Line', lineStyle='Dot')
    plot.scatter(xx, yy, oplot=1, pointRep='Line', color='red')
