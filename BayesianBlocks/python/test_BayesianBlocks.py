import sys
import time
import BayesianBlocks

evts = []
file = open("../data/events.dat")
for line in file:
    evts.append(float(line.strip()))

my_blocks = BayesianBlocks.BayesianBlocks(evts)

ncpPrior = 1

if len(sys.argv) == 2:
    ncpPrior = float(sys.argv[1])

t0 = time.time()

x, y = my_blocks.lightCurve(ncpPrior)

t1 = time.time()

print t1 - t0

import hippoplotter as plot

plot.clear()
plot.histogram(evts)
plot.scatter(x, y, pointRep='Line', oplot=1, color='red')
