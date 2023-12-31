import numpy as num
from BayesBlocks import BayesBlocks, LightCurve

from distributions import sample, stepFunction

nsamp = 200
events = sample(stepFunction(0.5, 0.7, amp=0.5), nsamp)

blocks = BayesBlocks(events)

x, y = blocks.lightCurve(1)
xx, yy = blocks.lightCurve(4)

import hippoplotter as plot
hist = plot.histogram(events, 'x')
reps = hist.getDataReps()
reps[0].setErrorDisplay('y', 1)

plot.scatter(x, y, pointRep='Line', oplot=1, color='red')
plot.scatter(xx, yy, pointRep='Line', oplot=1, color='green')
