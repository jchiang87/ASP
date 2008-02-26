"""
@brief Region-of-intereset source analysis for DRP monitoring.  This
will be performed for the 100 MeV -- 300 GeV range and will provide
the fluxes for determining if a non-DRP source is in a state where it
should have its data made public.

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
import databaseAccess as dbAccess

debug = False

id = int(os.environ['ROI_ID']) - 1
name = rois[id].name
os.chdir(name)

ft1file = name + '_events.fits'
srcModel = os.path.join(os.getcwd(), name + '_model.xml')

gtselect = GtApp('gtselect')
gtselect.run(infile=ft1file, outfile=name+'_100_300000.fits', 
             radius=180, emin=100, emax=300000)

if debug:
    print "analyzing ", ft1file, srcModel
else:
#
# run gtdiffrsp locally for each region until the full sky
# diffuseResponses process is parallelized
#
    gtdiffrsp = GtApp('gtdiffrsp')
    gtdiffrsp['evfile'] = gtselect['outfile']
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
    sql = "select eband_id, emin, emax from ENERGYBANDS"
    def getEnergyBands(cursor):
        ids, emins, emaxs = [], [], []
        for entry in cursor:
            if not (entry[1]==100 and entry[2]==300000):
                ids.append("%i", entry[0])
                emins.append("%i" % entry[1])
                emaxs.append("%i" % entry[2])
        ids = ' '.join(ids)
        emins = ' '.join(emins)
        emaxs = ' '.join(emaxs)
        return ids, emins, emaxs
    ids, emins, emaxs = dbAccess.apply(sql, getEnergyBands)
    pipeline.setVariable('EBAND_IDS', ids)
    pipeline.setVariable('MINIMUM_ENERGIES', emins)
    pipeline.setVariable('MAXIMUM_ENERGIES', emaxs)
            
    os.system('chmod 777 *')
