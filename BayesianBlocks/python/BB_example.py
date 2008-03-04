import numarray as num
from BayesBlocks import BayesBlocks, LightCurve

from distributions import sample

npts = 100
phi = num.arange(npts, type=num.Float)/(npts-1)*2.*num.pi
func = 1. + num.sin(phi)

nsamp = 5000
events = sample(func, nsamp)*2.*num.pi

fine_blocks = BayesBlocks(events, 4)
#rough_blocks = BayesBlocks(events, 4)

fine_lc = LightCurve(fine_blocks.computeLightCurve())
#rough_lc = LightCurve(rough_blocks.computeLightCurve())

(x, y) = fine_lc.dataPoints()
#(xx, yy) = rough_lc.dataPoints()

import hippoplotter as plot
hist = plot.histogram(events, 'phi')
reps = hist.getDataReps()
reps[0].setErrorDisplay('y', 1)
plot.scatter(x, y, pointRep='Line', oplot=1, color='red')

#plot.scatter(xx, yy, pointRep='Line', oplot=1, lineStyle='Dash')

