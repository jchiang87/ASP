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
