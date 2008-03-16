"""
@brief Compute exposure-related data for extracted GRB afterglow data.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
from parfile_parser import parfile_parser

os.chdir(os.environ['OUTPUTDIR'])
grbName = parfile_parser(os.environ['GRBPARS'])['name']

afterglowFiles = grbName + '_afterglow_files'
pars = parfile_parser(afterglowFiles)

gtlivetimecube = GtApp('gtlivetimecube')
gtlivetimecube['evfile'] = pars['ft1File']
gtlivetimecube['scfile'] = pars['ft2File']
gtlivetimecube['outfile'] = 'expCube_' + grbName + '.fits'
#print gtlivetimecube.command()
gtlivetimecube.run()

gtexpmap = GtApp('gtexpmap')
gtexpmap['evfile'] = pars['ft1File']
gtexpmap['scfile'] = pars['ft2File']
gtexpmap['exposure_cube_file'] = gtlivetimecube['outfile']
gtexpmap['outfile'] = 'expmap_' + grbName + '.fits'
gtexpmap['source_region_radius'] = 25
gtexpmap['rspfunc'] = 'DSS'
#print gtexpmap.command()
gtexpmap.run()

gtdiffresp = GtApp('gtdiffresp')
gtdiffresp['evfile'] = pars['ft1File']
gtdiffresp['scfile'] = pars['ft2File']
gtdiffresp['source_model_file'] = pars['xmlFile']
gtdiffresp['rspfunc'] = 'DSS'
#print gtdiffresp.command()
gtdiffresp.run()

output = open(afterglowFiles, 'a')
output.write('expcube = %s\n' % gtlivetimecube['outfile'])
output.write('expmap = %s\n' % gtexpmap['outfile'])
output.close()
