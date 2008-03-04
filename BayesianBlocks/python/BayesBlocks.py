import numarray as num
import bisect
from BayesianBlocks import BayesianBlocks, DoubleVector

class BayesBlocks(BayesianBlocks):
    def __init__(self, events, ncpPrior=1):
        BayesianBlocks.__init__(self, events, ncpPrior)
    def setCellScaling(self, scaleFactors):
        BayesianBlocks.setCellScaling(self, scaleFactors)
    def lightCurve(self):
        return LightCurve(BayesianBlocks.lightCurve(self))
    def _computeLightCurve(self):
        tmins = DoubleVector()
        tmaxs = DoubleVector()
        numEvents = DoubleVector()
        BayesianBlocks.computeLightCurve(self, tmins, tmaxs, numEvents)
        return num.array(tmins), num.array(tmaxs), num.array(numEvents)
    def cells(self):
        my_cells = DoubleVector()
        self.getCells(my_cells)
        return num.array(my_cells)
    def cellBoundaries(self, scaled=True):
        my_boundaries = DoubleVector()
        self.getCellBoundaries(my_boundaries, scaled)
        return num.array(my_boundaries)

def retrend(lightCurve, spectrum):
    tmins, tmaxs, numEvents = lightCurve
    energies = []
    dens = []
    ecenter = []
    for tmin, tmax, numEvts in zip(tmins, tmaxs, numEvents):
        my_dens = numEvts/(tmax - tmin)
        if (tmin < 0):
            energies.append(min(events))
        else:
            energies.append(tmin)
        energies.append(tmax)
        dens.extend([my_dens, my_dens])
        ecenter.extend([num.sqrt(tmin*tmax), num.sqrt(tmin*tmax)])
    energies = num.array(energies)
    ecenter = num.array(ecenter)
    jacobian = lambda en : abs(spectrum(en) + en*spectrum.deriv(en))
    dens = num.array(dens)*jacobian(energies)/jacobian(ecenter)
    return energies, dens

class LightCurve(object):
    def __init__(self, lightCurveData):
        tmins, tmaxs, numEvents = lightCurveData
        self.times = []
        self.dens = []
        for tmin, tmax, numEvts in zip(tmins, tmaxs, numEvents):
            my_dens = numEvts/(tmax - tmin)
            self.times.extend([tmin, tmax])
            self.dens.extend([my_dens, my_dens])
    def __call__(self, t):
        try:
            y = []
            for x in t:
                indx = min(len(self.times)-1, bisect.bisect(self.times, x))
                y.append(self.dens[indx])
            return y
        except TypeError:
            indx = bisect.bisect(self.times, t)
            return self.dens[indx]
        return y
    def dataPoints(self):
        return self.times, self.dens

