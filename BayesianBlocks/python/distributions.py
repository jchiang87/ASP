import bisect
import random
import numarray as num

def integralDist(dist):
    my_integralDist = [0]
    for entry in dist:
        my_integralDist.append(my_integralDist[-1] + entry)
    my_integralDist = num.array(my_integralDist)/my_integralDist[-1]
    return my_integralDist

def interpolate(x, y, xx):
    i = bisect.bisect(x, xx) - 1
    i = min(len(x)-2, i)
    if x[i+1] == x[i]: return (y[i+1] + y[i])/2.
    return (xx - x[i])/(x[i+1] - x[i])*(y[i+1] - y[i]) + y[i]

def sample(dist, nsamp):
    my_integralDist = integralDist(dist)
    values = num.arange(len(dist)+1, type=num.Float)/float(len(dist))
    my_sample = []
    for i in range(nsamp):
        xi = random.random()
        my_sample.append(interpolate(my_integralDist, values, xi))
    return num.array(my_sample)

def stepFunction(x1, x2, npts=50, amp=0.5):
    xx = num.arange(npts)/float(npts-1)
    yy = []
    for xval in xx:
        if xval < x1:
            yy.append(1. - amp)
        elif xval < x2:
            yy.append(1.)
        else:
            yy.append(1. - amp)
    return yy

def uniq(x):
    y = {}
    for xx in x:
        if not y.has_key(xx):
            y[xx] = 1
    return y.keys()
