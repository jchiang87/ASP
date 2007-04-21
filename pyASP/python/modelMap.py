#!/usr/bin/env python

"""
@brief Make model maps.

@author W. Focke <focke@slac.stanford.edu>
"""

import os

from GtApp import GtApp
from parfile_new import Parfile

debug = False

output_dir = os.environ['output_dir']
os.chdir(output_dir)

gtmodelmap = GtApp('gtmodelmap')

pars = Parfile()

gtmodelmap['srcmaps'] = pars['source_map']
gtmodelmap['source_model_file'] = pars['model_file']
gtmodelmap['outfile'] = 'modelMap.fits'

pars['model_map'] = gtmodelmap['outfile']
pars.write()

if debug:
    print gtmodelmap.command()
else:
    gtmodelmap.run()
