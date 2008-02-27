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
from FitsNTuple import FitsNTuple
from SourceData import SourceData
from computeUpperLimit import computeUpperLimit

gtselect = GtApp('gtselect')

def currentRoi():
    id = int(os.environ['ROI_ID']) - 1
    return rois[id]

def fitEnergyBand(emin, emax, srcModel):
    gtselect['infile'] = currentRoi().name + '_events.fits'
    gtselect['outfile'] = 'events_%i_%i.fits' % (emin, emax)
    gtselect['rad'] = 180
    gtselect['emin'] = emin
    gtselect['emax'] = emax
    gtselect.run()

    foo = FitsNTuple(gtselect['outfile'])
    if len(foo.TIME) == 0:
        print "no events in this energy band, (%e, %e)" % (emin, emax)
        return None

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
            flux = computeUpperLimit(like, srcname)
            isUL = True
        results[srcname] = SourceData(srcname, flux, fluxerr, outputModel, isUL)
    return results

if __name__ == '__main__':
    from MonitoredSources import drpSources, blazars
    
    roi = currentRoi()
    os.chdir(roi.name)

    inputModel = "%s_%i_%i_model.xml" % (currentRoi().name, 100, 300000)
    srcModel = os.path.join(os.getcwd(), inputModel)
    emin = float(os.environ['emin'])
    emax = float(os.environ['emax'])

    results = fitEnergyBand(emin, emax, srcModel)
    
    if results is not None:
        drp_list = drpSources.select(roi.ra, roi.dec, roi.radius)
        drp_list.extend(blazars.select(roi.ra, roi.dec, roi.radius))

        for src in drp_list:
            print src
            results[src].insertDbEntry()
            
    os.system('chmod o+w *')
