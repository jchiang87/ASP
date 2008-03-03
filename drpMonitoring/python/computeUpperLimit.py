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

def computeUpperLimit(like, source, parname='Integral', delta=2.71/2.,
                      tmpfile='temp_model.xml'):
    saved_pars = [par.value() for par in like.model.params]
    par = like[source].funcs['Spectrum'].getParam(parname)
    logLike0 = like()
    x0 = par.getTrueValue()
    dx = par.error()*par.getScale()
    return x0 + 2*dx  # kluge for now

# The implementation below does the right thing for simple source
# models, but tends to run forever for complicated source models.
#
#    if dx == 0:
#        dx = x0
#    xvals, dlogLike = [], []
#    par.setFree(0)
#    for x in num.arange(x0, x0 + 3*dx, 3*dx/30):
#        xvals.append(x)
#        par.setValue(x)
#        like.logLike.syncSrcParams(source)
#        try:
#            like.fit(0)
#        except RuntimeError:
#            try:
#                like.fit(0)
#            except RuntimeError:
#                like.logLike.restoreBestFit()
#                pass
#        dlogLike.append(like()-logLike0)
#        if dlogLike[-1] > delta:
#            break
#    par.setFree(1)
#    for value, param in zip(saved_pars, like.model.params):
#        param.setValue(value)
#    xx = ((delta - dlogLike[-2])/(dlogLike[-1] - dlogLike[-2])
#          *(xvals[-1] - xvals[-2]) + xvals[-2])
#    return xx*par.getScale()
