"""
@brief Region-of-intereset source analysis for DRP monitoring.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
import pipeline
from GtApp import GtApp
from UnbinnedAnalysis import *
from drpRoiSetup import rootpath, pars, rois, output_dir

debug = False

id = int(os.environ['ROI_ID']) - 1
name = rois[id].name
os.chdir(name)

ft1file = name + '_events.fits'
srcModel = os.path.join(os.getcwd(), name + '_model.xml')

if debug:
    print "analyzing ", ft1file, srcModel
else:
#
# run gtdiffrsp locally for each region until the full sky
# diffuseResponses process is parallelized
#
    gtdiffrsp = GtApp('gtdiffrsp')
    gtdiffrsp['evfile'] = ft1file
    gtdiffrsp['scfile'] = pars['ft2file']
    gtdiffrsp['irfs'] = pars['rspfunc']
    gtdiffrsp['srcmdl'] = rootpath('diffuse_model.xml')
    gtdiffrsp.run()

    irfs = pars['rspfunc']
    if irfs == 'DSS':
        irfs = 'DC2'
    obs = UnbinnedObs(ft1file, pars['ft2file'], expMap=pars['expMap'],
                      expCube=pars['expCube'], irfs=irfs)
    like = UnbinnedAnalysis(obs, srcModel, 'Minuit')
#    like = UnbinnedAnalysis(obs, srcModel, 'Drmnfb')

    try:
        like.fit()
    except RuntimeError:
        try:
            like.fit()
        except RuntimeError:
            pass

    print like.model
    outputModel = name + '_model_out.xml'
    like.writeXml(outputModel)

#
# query the db tables and write the energy bands that the pipeline
# needs to dispatch for analysis
#
    sql = "select * from ENERGYBANDS"
    def getEnergyBands(cursor):
        emins = []
        emaxs = []
        for entry in cursor:
            emins.append("%i" % entry[2])
            emaxs.append("%i" % entry[3])
        emins = ' '.join(emins)
        emaxs = ' '.join(emaxs)
        return emins, emaxs
    emins, emax = apply(sql, getEnergyBands)
    pipeline.setVariable('MINIMUM_ENERGIES', emins)
    pipeline.setVariable('MAXIMUM_ENERGIES', emaxs)
            
    os.system('chmod 777 *')
