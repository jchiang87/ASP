import numarray as num
from BayesBlocks import BayesBlocks, LightCurve

from distributions import sample, stepFunction

nsamp = 200
events = sample(stepFunction(0.5, 0.7, amp=0.5), nsamp)

fine_blocks = BayesBlocks(events, 1)
#rough_blocks = BayesBlocks(events, 4)

fine_lc = LightCurve(fine_blocks.computeLightCurve())
#rough_lc = LightCurve(rough_blocks.computeLightCurve())

(x, y) = fine_lc.dataPoints()
#(xx, yy) = rough_lc.dataPoints()

import hippoplotter as plot
hist = plot.histogram(events, 'x')
reps = hist.getDataReps()
reps[0].setErrorDisplay('y', 1)
plot.scatter(x, y, pointRep='Line', oplot=1, color='red')

#plot.scatter(xx, yy, pointRep='Line', oplot=1, lineStyle='Dash')

