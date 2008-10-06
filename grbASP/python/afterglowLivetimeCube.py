"""
@brief Compute exposure-related data for extracted GRB afterglow data.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
from parfile_parser import Parfile
from combineExpMaps import writeExpMapBounds
from GrbAspConfig import grbAspConfig, irf_config

debug = False
#debug = True

os.chdir(os.environ['OUTPUTDIR'])
grbpars = Parfile(os.environ['GRBPARS'])

config = grbAspConfig.find(grbpars['tstart'])
print config

grbName = grbpars['name']

afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

gtlivetimecube = GtApp('gtltcube', 'Likelihood')
gtlivetimecube['evfile'] = pars['ft1File']
gtlivetimecube['scfile'] = pars['ft2File']
gtlivetimecube['outfile'] = 'expCube_' + grbName + '.fits'
if debug:
    print gtlivetimecube.command()
else:
    gtlivetimecube.run()

irfs, ft1_filter = irf_config(grbpars['tstart'])

gtexpmap = GtApp('gtexpmap', 'Likelihood')
gtexpmap['evfile'] = pars['ft1File']
gtexpmap['scfile'] = pars['ft2File']
gtexpmap['expcube'] = gtlivetimecube['outfile']
gtexpmap['outfile'] = 'expMap_' + grbName + '.fits'
gtexpmap['srcrad'] = config.AGRADIUS + 10
#gtexpmap['irfs'] = config.IRFS
gtexpmap['irfs'] = irfs
gtexpmap.pars.write(os.path.join(os.environ['OUTPUTDIR'], 'gtexpmap.par'))

writeExpMapBounds(gtexpmap, nx=1, ny=1)

output = open(afterglowFiles, 'a')
output.write('expcube = %s\n' % gtlivetimecube['outfile'])
output.write('expmap = %s\n' % gtexpmap['outfile'])
output.close()

os.system('chmod 777 *')
