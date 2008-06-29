import sys
import time
import BayesianBlocks

evts = []
file = open("../data/events.dat")
for line in file:
    evts.append(float(line.strip()))

my_blocks = BayesianBlocks.BayesianBlocks(evts)

if len(sys.argv) == 2:
    my_blocks.setNcpPrior(float(sys.argv[1]))
t0 = time.time()
tmins, tmaxs, numEvents = my_blocks.lightCurve()
t1 = time.time()
print t1 - t0

import hippoplotter as plot

times = []
dens = []

for tmin, tmax, numEvts in zip(tmins, tmaxs, numEvents):
    my_dens = numEvts/(tmax - tmin)
    times.extend([tmin, tmax])
    dens.extend([my_dens, my_dens])

plot.clear()
#plot.histogram(evts, ylog=1)
plot.histogram(evts)
plot.scatter(times, dens, pointRep='Line', oplot=1, color='red')
