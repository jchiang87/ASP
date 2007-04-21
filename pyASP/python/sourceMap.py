#!/usr/bin/env python

"""
@brief Make source maps.

@author W. Focke <focke@slac.stanford.edu>
"""

import os

from GtApp import GtApp
from parfile_new import Parfile

debug = False

_ft2File = '/nfs/farm/g/glast/u33/jchiang/ASP/testdata/eg_diffuse_scData_0000.fits'

output_dir = os.environ['output_dir']
os.chdir(output_dir)

gtsrcmaps = GtApp('gtsrcmaps')

pars = Parfile()

gtsrcmaps['scfile'] = pars['ft2file']
gtsrcmaps['exposure_cube_file'] = pars['expCube']
gtsrcmaps['counts_map_file'] = pars['count_map']
gtsrcmaps['source_model_file'] = pars['model_file']
gtsrcmaps['binned_exposure_map'] = 'binned_exposure.fits'
gtsrcmaps['outfile'] = 'sourceMap.fits'
gtsrcmaps['chatter'] = 4

pars['source_map'] = gtsrcmaps['outfile']
pars.write()

if debug:
    print gtsrcmaps.command()
else:
    gtsrcmaps.run()
