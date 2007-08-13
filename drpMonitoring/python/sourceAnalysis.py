"""
@brief Region-of-intereset source analysis for DRP monitoring.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
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
# run gtdiffresp locally for each region until the full sky
# diffuseResponses process is parallelized
#
    gtdiffresp = GtApp('gtdiffrsp')
    gtdiffresp['evfile'] = ft1file
    gtdiffresp['scfile'] = pars['ft2file']
    gtdiffresp['irfs'] = pars['rspfunc']
    gtdiffresp['srcmdl'] = rootpath('diffuse_model.xml')
    gtdiffresp.run()

    irfs = pars['rspfunc']
    if irfs == 'DSS':
        irfs = 'DC2'
    obs = UnbinnedObs(ft1file, pars['ft2file'], expMap=pars['expMap'],
                      expCube=rootpath(pars['expCube']), irfs=irfs)
#    like = UnbinnedAnalysis(obs, srcModel, 'Minuit')
    like = UnbinnedAnalysis(obs, srcModel, 'Drmnfb')

    try:
        like.fit()
    except RuntimeError:
        try:
            like.fit()
        except RuntimeError:
            pass
    outputModel = name + '_model_out.xml'
    like.writeXml(outputModel)
    
    os.system('chmod 777 *')
