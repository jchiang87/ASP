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
from drpRoiSetup import pars, currentRoi
import pyfits
from SourceData import SourceData, SourceTypeError
from computeUpperLimit import computeUpperLimit
import drpDbAccess

gtselect = GtApp('gtselect')

def fitEnergyBand(emin, emax, srcModel, roi):
    gtselect['infile'] = roi.name + '_events.fits'
    gtselect['outfile'] = 'events_%i_%i.fits' % (emin, emax)
    gtselect['rad'] = 180
    gtselect['emin'] = emin
    gtselect['emax'] = emax
    gtselect.run()

    foo = pyfits.open(gtselect['outfile'])
    if foo[1].data is None:
        print "No events in this energy band, (%e, %e)" % (emin, emax)
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

    outputModel = "%s_%i_%i_model.xml" % (roi.name, emin, emax)
    like.srcModel = outputModel
    like.writeXml()
    like.state(open("analysis_%i_%i.py" % (emin, emax), "w"))

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
        try:
            results[srcname] = SourceData(srcname, flux, fluxerr, 
                                          outputModel, isUL)
        except SourceTypeError:
            pass

    #
    # Write the results to the LIGHTCURVES database tables. Here we
    # select only those sources to write for which this is the
    # principal ROI as given by its POINTSOURCES table ROI_ID entry.
    #
    monitored_list = drpDbAccess.findPointSources(0, 0, 180).select(roi.id)

    print "Writing db table entries for "
    for src in monitored_list:
        print src
        try:
            results[src].insertDbEntry()
        except KeyError:
            print src, "not found in this ROI"

    return results

if __name__ == '__main__':
    roi = currentRoi()
    os.chdir(roi.name)

    inputModel = "%s_%i_%i_model.xml" % (currentRoi().name, 100, 300000)
    srcModel = os.path.join(os.getcwd(), inputModel)
    emin = float(os.environ['emin'])
    emax = float(os.environ['emax'])

    fitEnergyBand(emin, emax, srcModel, roi)
            
    os.system('chmod o+w *')
