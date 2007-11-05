"""
@brief Fit specific energy bands.  This has been separated from
sourceAnalysis.py, which fits the broadest energy range, so that
instances of this script can be tracked as a separate processes in the
pipeline and run in parallel.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
from GtApp import GtApp
from UnbinnedAnalysis import *
from drpRoiSetup import rootpath, pars, rois, output_dir
from DbEntry import DbEntry

gtselect = GtApp('gtselect')

def currentRoi():
    id = int(os.environ['ROI_ID']) - 1
    return rois[id]

class SourceData(object):
    def __init__(self, name, srcModel, emin, emax, flux, fluxerr, isUL=False):
        self.name = name
        self.srcModel = srcModel
        self.emin, self.emax = emin, emax
        self.flux, self.fluxerr = flux, fluxerr
        self.isUL = isUL
    def updateDbEntry(self):
        variable = "flux_%i_%i" % (self.emin, self.emax)
        dbEntry = DbEntry(self.name, variable, pars['start_time'],
                          pars['stop_time'])
        dbEntry.setValues(self.flux, self.fluxerr, isUpperLimit=self.isUL)
        dbEntry.setXmlFile(self.srcModel)
        dbEntry.write()
        print "Writing database entry for %s." % self.name
        print "%s = %e +/- %e" % (variable, self.flux, self.fluxerr)
        print "time period: %s to %s" % (pars['start_time'], pars['stop_time'])


def upperLimit(like, source, parname='Integral', delta=2.71/2.,
               tmpfile='temp_model.xml'):
    like.writeXml(tmpfile)
    par = like[source].funcs['Spectrum'].getParam(parname)
    logLike0 = like()
    x0 = par.value()
    dx = par.error()
    xvals, dlogLike = [], []
    par.setFree(0)
    for x in num.arange(x0, x0 + 3*dx, 3*dx/30):
        xvals.append(x)
        par.setValue(x)
        like.logLike.syncSrcParams(source)
        like.fit(0)
        dlogLike.append(like()-logLike0)
        if dlogLike[-1] > delta:
            break
    like.logLike.reReadXml(tmpfile)
    try:
        os.remove(tmpfile)
    except OSError:
        pass
    xx = ((delta - dlogLike[-2])/(dlogLike[-1] - dlogLike[-2])
          *(xvals[-1] - xvals[-2]) + xvals[-2])
    return xx*par.getScale()

def fitEnergyBand(emin, emax, srcModel):
    gtselect['infile'] = currentRoi().name + '_events.fits'
    gtselect['outfile'] = 'events_%i_%i.fits' % (emin, emax)
    gtselect['rad'] = 180
    gtselect['emin'] = emin
    gtselect['emax'] = emax
    gtselect.run()

    irfs = pars['rspfunc']
    if irfs == 'DSS':
        irfs = 'DC2'

    obs = UnbinnedObs(gtselect['outfile'], pars['ft2file'],
                      expMap=pars['expMap'],
                      expCube=pars['expCube'],
                      irfs=irfs)
    like = UnbinnedAnalysis(obs, srcModel, 'Minuit')
    like.state(open("analysis_%i_%i.py" % (emin, emax), "w"))
    
    ptsrcs = []
    for srcname in like.model.srcNames:
        if like.model[srcname].src.getType() == 'Point':
            ptsrcs.append(srcname)

    for srcname in ptsrcs:
        src = like.model[srcname]
        lowerLimit = src.funcs['Spectrum'].getParam('LowerLimit')
        lowerLimit.parameter.setBounds(10, 5e5)
        lowerLimit.parameter.setValue(emin)
        upperLimit = src.funcs['Spectrum'].getParam('UpperLimit')
        upperLimit.parameter.setBounds(10, 5e5)
        upperLimit.parameter.setValue(emax)

    try:
        like.fit()
    except RuntimeError:
        try:
            like.fit()
        except RuntimeError:
            pass

    outputModel = "%s_%i_%i_model.xml" % (currentRoi().name, emin, emax)
    like.writeXml(outputModel)

    outputModel = os.path.join(os.getcwd(), outputModel)

    print like.model
    sys.stdout.flush()

    results = {}
    for srcname in ptsrcs:
        src = like.model[srcname]
        spec = src.funcs['Spectrum']
        integral = spec.getParam('Integral')
        flux = integral.getTrueValue()
        fluxerr = integral.error()*integral.getScale()
        isUL = False
        if like.Ts(srcname) < 25:
            flux = upperLimit(like, srcname)
            isUL = True
        results[srcname] = SourceData(srcname, outputModel, emin, emax,
                                      flux, fluxerr, isUL)
    return results

if __name__ == '__main__':
    from DrpSources import drpSources, blazars
    
    roi = currentRoi()
    os.chdir(roi.name)
    
    srcModel = os.path.join(os.getcwd(), roi.name + '_model_out.xml')
    emin = float(os.environ['emin'])
    emax = float(os.environ['emax'])

    results = fitEnergyBand(emin, emax, srcModel)
    
    drp_list = drpSources.select(roi.ra, roi.dec, roi.radius)
    drp_list.extend(blazars.select(roi.ra, roi.dec, roi.radius))

    for src in drp_list:
        print src
        results[src].updateDbEntry()

    
