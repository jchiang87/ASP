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
    def __init__(self, name, srcModel, emin, emax, flux, fluxerr):
        self.name = name
        self.srcModel = srcModel
        self.emin, self.emax = emin, emax
        self.flux, self.fluxerr = flux, fluxerr
    def updateDbEntry(self):
        variable = "flux_%i_%i" % (emin, emax)
        dbEntry = DbEntry(self.name, variable, pars['start_time'],
                          pars['stop_time'])
        dbEntry.setValues(flux, fluxerr)
        dbEntry.setMetaData("xmlFile", self.srcModel)

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
                      expCube=rootpath(pars['expCube']),
                      irfs=irfs)
    like = UnbinnedAnalysis(obs, srcModel, 'Minuit')

    like.state(open("analysis_%i_%i.py" % (emin, emax), "w"))
    
    ptsrcs = []
    for srcname in like.model.srcNames:
        if like.model[srcname].src.getType() == 'Point':
            ptsrcs.append(srcname)

    for srcname in ptsrcs:
        src = like.model[srcname]
#            flux_est = src.flux(emin, emax)
#            integral = src.funcs['Spectrum'].getParam('Integral')
#            integral.parameter.setTrueValue(flux_est)
        lowerLimit = src.funcs['Spectrum'].getParam('LowerLimit')
        lowerLimit.parameter.setValue(emin)
        upperLimit = src.funcs['Spectrum'].getParam('UpperLimit')
        upperLimit.parameter.setValue(emax)

#    print like.model
#    sys.stdout.flush()

    try:
        like.fit()
    except RuntimeError:
        like.fit()

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
        results[srcname] = SourceData(srcname, outputModel, emin, emax,
                                      flux, fluxerr)
    return results

if __name__ == '__main__':
    from DrpSources import drpSources
    
    roi = currentRoi()
    os.chdir(roi.name)
    
    srcModel = os.path.join(os.getcwd(), roi.name + '_model_out.xml')
    emin = float(os.environ['emin'])
    emax = float(os.environ['emax'])

    results = fitEnergyBand(emin, emax, srcModel)
    
    drp_list = drpSources.select(roi.ra, roi.dec, roi.radius)

#    for src in drp_list:
#        results[src].updateDbEntry()
