"""
@brief Compute diffuse response quantities for the GRB afterglow analysis.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
from parfile_parser import Parfile
from GrbAspConfig import grbAspConfig, irf_config
from addNdifrsp import addNdifrsp

debug = False

os.chdir(os.environ['OUTPUTDIR'])
grbpars = Parfile(os.environ['GRBPARS'])

config = grbAspConfig.find(grbpars['tstart'])
print config

irfs, ft1_filter = irf_config(grbpars['tstart'])

grbName = grbpars['name']
afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

gtdiffrsp = GtApp('gtdiffrsp', 'Likelihood')
gtdiffrsp['evfile'] = pars['ft1File']
gtdiffrsp['scfile'] = pars['ft2File']
gtdiffrsp['srcmdl'] = pars['xmlFile']
#gtdiffrsp['irfs'] = config.IRFS
gtdiffrsp['irfs'] = irfs
if debug:
    print gtdiffrsp.command()
else:
    addNdifrsp(gtdiffrsp['evfile'])
    gtdiffrsp.run()

os.system('chmod 777 *')
