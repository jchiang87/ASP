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

import os, sys, shutil
import pipeline
from GtApp import GtApp
from UnbinnedAnalysis import *
from drpRoiSetup import rootpath, pars, rois, output_dir
import databaseAccess as dbAccess
from fitEnergyBand import fitEnergyBand, currentRoi
from assignRois import RoiIds

roiIds = RoiIds(os.path.join(os.environ['OUTPUTDIR'], 'rois.txt'))

#
# Move to working directory for the ROI of interest
#
roi = currentRoi()
os.chdir(roi.name)
print "Working in ", os.getcwd

#
# Run gtdiffrsp locally for each region in case it hasn't been run by
# L1Proc.
#
gtdiffrsp = GtApp('gtdiffrsp')
gtdiffrsp['evfile'] = roi.name + '_events.fits'
gtdiffrsp['scfile'] = pars['ft2file']
gtdiffrsp['irfs'] = pars['rspfunc']
gtdiffrsp['srcmdl'] = rootpath('diffuse_model.xml')
gtdiffrsp.run()

#
# Fit the energy band (100, 300000) MeV to be used for determining the
# monitoring state of the non-DRP sources.
#
srcModel = os.path.join(os.getcwd(), roi.name + '_model.xml')
shutil.copy(srcModel, srcModel + '_input')
results = fitEnergyBand(100, 300000, srcModel, roi, roiIds)

#
# Query the db tables and write the energy bands that the pipeline
# needs to dispatch for subsequent analyses.
#
sql = "select eband_id, emin, emax from ENERGYBANDS where GROUP_ID=0"
def getEnergyBands(cursor):
    ids, emins, emaxs = [], [], []
    for entry in cursor:
        if not (entry[1]==100 and entry[2]==300000):
            ids.append("%i" % entry[0])
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

os.system('chmod o+w *')
