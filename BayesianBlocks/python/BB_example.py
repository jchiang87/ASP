import numpy as num
from BayesianBlocks import *
from BayesBlocks import BayesBlocks, LightCurve

from distributions import sample

npts = 100
phi = num.arange(npts, dtype=num.float)/(npts-1)*2.*num.pi
func = 1. + num.sin(phi)

ncp_prior = 8

nsamp = 5000
events = sample(func, nsamp)*2.*num.pi

fine_blocks = BayesBlocks(events)

x, y = fine_blocks.lightCurve(ncp_prior)

import hippoplotter as plot
hist = plot.histogram(events, 'phi')
reps = hist.getDataReps()
reps[0].setErrorDisplay('y', 1)
plot.scatter(x, y, pointRep='Line', oplot=1, color='red')

foo = BayesianBlocks(events)
xx, yy = foo.lightCurve(ncp_prior)
plot.scatter(xx, yy, pointRep='Line', oplot=1, color='green')
