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

debug = False

os.chdir(os.environ['OUTPUTDIR'])
grbName = Parfile(os.environ['GRBPARS'])['name']

afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

gtdiffresp = GtApp('gtdiffrsp', 'Likelihood')
gtdiffresp['evfile'] = pars['ft1File']
gtdiffresp['scfile'] = pars['ft2File']
gtdiffresp['source_model_file'] = pars['xmlFile']
gtdiffresp['rspfunc'] = 'DSS'
if debug:
    print gtdiffresp.command()
else:
    gtdiffresp.run()

os.system('chmod 777 *')
