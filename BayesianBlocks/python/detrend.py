import random
import numarray as num
from BayesBlocks import BayesBlocks, retrend

class Distribution(object):
    def generateEvents(self, nevents=1000):
        events = []
        for i in xrange(nevents):
            events.append(self.draw())
        return events

class PowerLaw(Distribution):
    def __init__(self, gamma=2, emin=20., emax=2e5, escale=1):
        self.gamma = gamma
        self.emin = emin/escale
        self.emax = emax/escale
        self.escale = escale
        self.eminGam = self.emin**(1. - gamma)
        self.emaxGam = self.emax**(1. - gamma)
    def draw(self):
        xi = random.random()
        ee = (xi*(self.eminGam - self.emaxGam)
              + self.emaxGam)**(1./(1. - self.gamma))
        return ee*self.escale
    def __call__(self, ee):
        return (ee/self.escale)**(-self.gamma)
    def deriv(self, ee):
        return -self.gamma*(ee/self.escale)**(-self.gamma - 1.)*self.escale
    def integral(self, emin, emax):
        if self.gamma != 1:
            return ((emin/self.escale)**(1. - self.gamma)
                    - (emax/self.escale)**(1. - self.gamma))/(self.gamma - 1.) 
        else:
            return num.log(emax/emin)

class BrokenPowerLaw(Distribution):
    def __init__(self, gamma1=1.7, ebreak=250., gamma2=2.2,
                 emin=20., emax=2e5):
        self.gamma1 = gamma1
        self.ebreak = ebreak
        self.gamma2 = gamma2
        self.emin = emin
        self.emax = emax
        self.pl1 = PowerLaw(gamma1, emin=emin, emax=ebreak,
                                    escale=ebreak)
        self.pl2 = PowerLaw(gamma2, emin=ebreak, emax=emax,
                                    escale=ebreak)
        self.brk = (self.pl1.integral(emin, ebreak)
                      /(self.pl1.integral(emin, ebreak)
                        + self.pl2.integral(ebreak, emax)))
    def draw(self):
        xi = random.random()
        if xi < self.brk:
            return self.pl1.draw()
        else:
            return self.pl2.draw()
    def __call__(self, ee):
        try:
            if ee < self.ebreak:
                return self.pl1(ee)
            else:
                return self.pl2(ee)
        except RuntimeError:
            result = []
            for energy in ee:
                result.append(self(energy))
            return num.array(result)
    def deriv(self, ee):
        try:
            if ee < self.ebreak:
                return self.pl1.deriv(ee)
            else:
                return self.pl2.deriv(ee)
        except RuntimeError:
            result = []
            for energy in ee:
                result.append(self.deriv(energy))
            return num.array(result)
    def integral(self, emin, emax):
        if emax < self.ebreak:
            return self.pl1.integral(emin, emax)
        elif emin < self.ebreak:
            return (self.pl1.integral(emin, self.ebreak)
                    + self.pl2.integral(self.ebreak, emax))
        else:
            return self.pl2.integral(emin, emax)
    
class Gaussian(Distribution):
    def __init__(self, mean, sigma):
        self.mean = mean
        self.sigma = sigma
    def draw(self):
        return random.gauss(self.mean, self.sigma)
    def __call__(self, ee):
        return (num.exp(-((ee-self.mean)/2./self.sigma)**2)
                /num.sqrt(2.)/self.sigma)

if __name__ == "__main__":
    import string, sys, time
    if len(sys.argv) == 2:
        ncpPrior = string.atof(sys.argv[1])
    else:
        ncpPrior = 2.

    import hippoplotter as plot
    gamma = 2.
    spectrum = PowerLaw(gamma=gamma)
#    spectrum = BrokenPowerLaw(gamma1=1.5, ebreak=200.)
    events = spectrum.generateEvents(1000)
    eline = 200.
    width = 30.
    gauss = Gaussian(eline, width)
    events.extend(gauss.generateEvents(50))
    events.sort()

    events = num.array(events)
    my_blocks = BayesBlocks(events.tolist(), ncpPrior)
    
    scaleFactors = spectrum(events)
    my_blocks.setCellScaling(scaleFactors.tolist())

    t0 = time.time()
    lightCurve = my_blocks.computeLightCurve()
    t1 = time.time()
    print t1 - t0

    energies, dens = retrend(lightCurve, spectrum)
    
    plot.clear()
    specHist = plot.histogram(events, 'energy', xlog=1, ylog=1)
    plot.canvas.selectDisplay(specHist)
    plot.scatter(energies, dens, oplot=1, pointRep='Line', color='red')
    plot.vline(eline)
    
