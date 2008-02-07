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
from combineExpMaps import writeExpMapBounds

debug = False
#debug = True

os.chdir(os.environ['OUTPUTDIR'])
grbName = parfile_parser(os.environ['GRBPARS'])['name']

afterglowFiles = grbName + '_afterglow_files'
pars = parfile_parser(afterglowFiles)

gtlivetimecube = GtApp('gtlivetimecube')
gtlivetimecube['evfile'] = pars['ft1File']
gtlivetimecube['scfile'] = pars['ft2File']
gtlivetimecube['outfile'] = 'expCube_' + grbName + '.fits'
if debug:
    print gtlivetimecube.command()
else:
    gtlivetimecube.run()

gtexpmap = GtApp('gtexpmap')
gtexpmap['evfile'] = pars['ft1File']
gtexpmap['scfile'] = pars['ft2File']
gtexpmap['exposure_cube_file'] = gtlivetimecube['outfile']
gtexpmap['outfile'] = 'expMap_' + grbName + '.fits'
gtexpmap['source_region_radius'] = 25
gtexpmap['rspfunc'] = 'DSS'
gtexpmap.pars.write('gtexpmap.par')
writeExpMapBounds()

output = open(afterglowFiles, 'a')
output.write('expcube = %s\n' % gtlivetimecube['outfile'])
output.write('expmap = %s\n' % gtexpmap['outfile'])
output.close()
