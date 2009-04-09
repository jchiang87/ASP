import sys, string, time
import numpy as num
import hippoplotter as plot
from distributions import *
from global_opt import global_opt
from EventData import EventData

def timing_study(ncp_prior):
    npts = 30.*num.exp(num.arange(10)/9.*num.log(1e3/30.))
    npts = num.array(npts, type=num.Int)
    num_timing = []
    py_timing = []
    for ndata in npts:
        events = sample(stepFunction(0.3, 0.6), ndata)
        evtData = EventData(events)
        cell_data = (num.array(evtData.cellSizes()),
                     num.ones(len(evtData.events), type=num.Float))
        
        t0 = time.time()
        change_points, best, last = global_opt(cell_data, ncp_prior)
        t1 = time.time()
        num_timing.append(t1 - t0)
        
        t0 = time.time()
        cp, bst, lst = evtData.globalOpt(ncp_prior)
        t1 = time.time()
        py_timing.append(t1 - t0)
        print ndata, num_timing[-1], py_timing[-1]
    plot.scatter(npts, num_timing, xlog=1, ylog=1)
    plot.scatter(npts, py_timing, oplot=1, color='red')

if __name__ == '__main__':
    timing_study(1)
