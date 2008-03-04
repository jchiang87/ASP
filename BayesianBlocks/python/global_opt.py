import numarray as num
import numarray.ma as ma
from gammaln import gammln

num.Error.setMode(invalid='ignore')

eps = 1e-16

def log_post(cell_data):
    (cell_sizes, cell_pops) = cell_data
    arg = cell_sizes - cell_pops + 1.
    arg = ma.masked_less_equal(arg, 0.)
    log_prob = ma.array( (gammln(cell_pops + 1.) + gammln(arg.raw_data())
                          + gammln(cell_sizes + 2.)), mask=arg.mask(),
                         fill_value=eps ).filled()
    return log_prob

def reverse(x):
    x = x.tolist()
    x.reverse()
    return num.array(x)

def extend(x, y):
    x = x.tolist()
    x.extend(y)
    return num.array(x)

def global_opt(cell_data, ncp_prior):
    npts = len(cell_data[0])
    best = []
    last = []
    for R in xrange(1, npts):
        qq = (num.cumsum(reverse(cell_data[0][:R])),
              num.cumsum(reverse(cell_data[1][:R])))
        tmp = [0]
        tmp.extend(best)
        results = tmp + reverse(log_post(qq)) - ncp_prior
        best.append(max(results))
        last.append(results.tolist().index(best[-1]))
    indx = last[-1]
    change_points = []
    while indx > 1:
        change_points.insert(0, indx)
        indx = last[indx-1]
    return change_points, best, last

if __name__ == '__main__':
    import sys, time
    from EventData import EventData
    from distributions import *
    #npts = 100
    #events = sample(stepFunction(0.3, 0.6), npts)*100.
    events = 'events.dat'
    evtData = EventData(events)
    cell_data = (num.array(evtData.cellSizes()),
                 num.ones(len(evtData.events), type=num.Float))
    try:
        ncp_prior = string.atof(sys.argv[1])
    except:
        ncp_prior = 1

    t0 = time.time()
    change_points, best, last = global_opt(cell_data, ncp_prior)
    t1 = time.time()
    print t1 - t0

    import hippoplotter as plot
    plot.clear()
    plot.histogram(evtData.events, 'event times', ylog=1)
    xx, yy = evtData.lightCurve(change_points)
    plot.scatter(xx, yy, oplot=1, pointRep='Line')

    t0 = time.time()
    cp, bst, lst = evtData.globalOpt(ncp_prior)
    t1 = time.time()
    print t1 - t0

    xx, yy = evtData.lightCurve(cp)
    plot.scatter(xx, yy, oplot=1, pointRep='Line', color='red')
                 
