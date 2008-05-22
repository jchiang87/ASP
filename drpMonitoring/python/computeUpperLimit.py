"""
@file computeUpperLimit.py

@brief Compte upperlimit for a source correponsing to a change in the
log-likelihood of delta. The default value of 2.71/2. corresponds to a
2-sigma UL.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import pyLikelihood as pyLike
import numpy as num

class ULResult(object):
    def __init__(self, value, emin, emax, delta, fluxes, dlogLike, parvalues):
        self.value = value
        self.emin, self.emax = emin, emax
        self.delta = delta
        self.fluxes, self.dlogLike, self.parvalues = fluxes, dlogLike, parvalues
    def __repr__(self):
        return ("%.2e ph/cm^2/s for emin=%.1f, emax=%.1f, delta(logLike)=%.2f"
                % (self.value, self.emin, self.emax, self.delta))

class UpperLimit(object):
    def __init__(self, like, source):
        self.like = like
        self.source = source
        self.results = []
    def compute(self, emin=100, emax=3e5, delta=2.71/2., 
                tmpfile='temp_model.xml', fix_src_pars=False,
                verbose=True, nsigmax=5, npts=30, renorm=False):
        source = self.source
        saved_pars = [par.value() for par in self.like.model.params]

        # Fix the normalization parameter for the scan.
        src_spectrum = self.like[source].funcs['Spectrum']
        par = src_spectrum.normPar()
        par.setFree(0)

        # For weak sources that use the PowerLaw model where the
        # reference energy is too low or that use the PowerLaw2 model
        # where the lower energy bound is too low, there can be a
        # strong correlation of the normalization parameter with the
        # photon index.  In this case, one can try to fix the other
        # source parameters to get a more stable upper limit. In
        # practice, one should reset the reference energy or lower
        # energy bound.
        if fix_src_pars:
            freePars = pyLike.ParameterVector()
            src_spectrum.getFreeParams(freePars)
            for item in freePars:
                src_spectrum.parameter(item.getName()).setFree(0)

        logLike0 = self.like()
        x0 = par.getValue()
        dx = par.error()

        if dx == 0:
            dx = x0
        xvals, dlogLike, fluxes = [], [], []
        if verbose:
            print self.like.model
        for i, x in enumerate(num.arange(x0, x0+nsigmax*dx, nsigmax*dx/npts)):
            xvals.append(x)
            par.setValue(x)
            self.like.logLike.syncSrcParams(source)
            self.fit(renorm=renorm)
            dlogLike.append(self.like() - logLike0)
            fluxes.append(self.like[source].flux(emin, emax))
            if verbose:
                print i, x, dlogLike[-1], fluxes[-1]
            if dlogLike[-1] > delta:
                break
            if len(dlogLike) > 2 and dlogLike[-1] < dlogLike[-2]:
                xvals.pop()
                dlogLike.pop()
                break
        par.setFree(1)
        if fix_src_pars:
            for item in freePars:
                src_spectrum.parameter(item.getName()).setFree(1)
        for value, param in zip(saved_pars, self.like.model.params):
            param.setValue(value)
        self.resync()
            
        xx = ((delta - dlogLike[-2])/(dlogLike[-1] - dlogLike[-2])
              *(xvals[-1] - xvals[-2]) + xvals[-2])
        ul = ((delta - dlogLike[-2])/(dlogLike[-1] - dlogLike[-2])
              *(fluxes[-1] - fluxes[-2]) + fluxes[-2])
        self.results.append(ULResult(ul, emin, emax, delta,
                                     fluxes, dlogLike, xvals))
        return ul
    def resync(self):
        srcNames = self.like.sourceNames()
        for src in srcNames:
            self.like.logLike.syncSrcParams(src)
    def fit(self, renorm=False):
        if renorm:
            self.renorm()
            return
        try:
            self.like.fit(0)
        except RuntimeError:
            try:
                self.like.fit(0)
            except RuntimeError:
                self.like.logLike.restoreBestFit()
                pass
    def renorm(self):
        freeNpred, totalNpred = self.npredValues()
        deficit = sum(self.like.nobs) - totalNpred
        renormFactor = 1. + deficit/freeNpred
        if renormFactor < 1:
            renormFactor = 1
        srcNames = self.like.sourceNames()
        for src in srcNames:
            parameter = self.like._normPar(src)
            if parameter.isFree():
                oldValue = parameter.getValue()
                newValue = oldValue*renormFactor
                xmin, xmax = parameter.getBounds()
                newValue = min(max(newValue, xmin), xmax)
                parameter.setValue(newValue)
        self.resync()
    def npredValues(self):
        srcNames = self.like.sourceNames()
        freeNpred = 0
        totalNpred = 0
        for src in srcNames:
            npred = self.like.logLike.NpredValue(src)
            totalNpred += npred
            if self.like._normPar(src).isFree():
                freeNpred += npred
        return freeNpred, totalNpred

class UpperLimits(dict):
    def __init__(self, like):
        dict.__init__(self)
        self.like = like
        for srcName in like.sourceNames():
            if self.like.logLike.getSource(srcName).getType() == "Point":
                self[srcName] = UpperLimit(like, srcName)
    
def computeUpperLimit(like, source, delta=2.71/2., tmpfile='temp_model.xml',
                      Ts_threshold=0):
    src_Ts = like.Ts(source)
    saved_pars = [par.value() for par in like.model.params]
    par = like[source].funcs['Spectrum'].normPar()
    par.setFree(0)

    if src_Ts < Ts_threshold:
        freePars = pyLike.ParameterVector()
        like[source].funcs['Spectrum'].getFreeParams(freePars)
        for item in freePars:
            like[source].funcs['Spectrum'].parameter(item.getName()).setFree(0)

    logLike0 = like()
    x0 = par.getValue()
    dx = par.error()

    if dx == 0:
        dx = x0
    xvals, dlogLike = [], []
    print like.model
    nsigmax = 3
    npts = 20
    for i, x in enumerate(num.arange(x0, x0 + nsigmax*dx, nsigmax*dx/npts)):
        xvals.append(x)
        par.setValue(x)
        like.logLike.syncSrcParams(source)
        try:
            like.fit(0)
        except RuntimeError:
            try:
                like.fit(0)
            except RuntimeError:
                like.logLike.restoreBestFit()
                pass
        dlogLike.append(like()-logLike0)
        print i, x, dlogLike[-1]
        if dlogLike[-1] > delta:
            break
    par.setFree(1)
    if src_Ts < Ts_threshold:
        for item in freePars:
            like[source].funcs['Spectrum'].parameter(item.getName()).setFree(1)
    for value, param in zip(saved_pars, like.model.params):
        param.setValue(value)
    like.fit(0)
    xx = ((delta - dlogLike[-2])/(dlogLike[-1] - dlogLike[-2])
          *(xvals[-1] - xvals[-2]) + xvals[-2])
    return xx*par.getScale()

if __name__ == '__main__':
    from analysis import like
#    like.fit()
    print computeUpperLimit(like, 'point source 0')
