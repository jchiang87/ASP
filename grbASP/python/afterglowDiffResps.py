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
from GrbAspConfig import grbAspConfig

debug = False

os.chdir(os.environ['OUTPUTDIR'])
grbpars = Parfile(os.environ['GRBPARS'])

config = grbAspConfig.find(grbpars['tstart'])
print config

grbName = grbpars['name']
afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

gtdiffresp = GtApp('gtdiffrsp', 'Likelihood')
gtdiffresp['evfile'] = pars['ft1File']
gtdiffresp['scfile'] = pars['ft2File']
gtdiffresp['srcmdl'] = pars['xmlFile']
gtdiffresp['irfs'] = config.IRFS
if debug:
    print gtdiffresp.command()
else:
    gtdiffresp.run()

os.system('chmod 777 *')
