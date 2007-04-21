"""
@brief Make difference maps.

DEPRECATED

@author W. Focke <focke@slac.stanford.edu>
"""

import os

from GtApp import GtApp
from parfile_parser import Parfile

farith = GtApp('farith')
 
parfile_basename = os.environ['PIPELINE_TASK'] + '.txt'
pars = Parfile(parfile_basename)

farith['infil1'] = pars['count_map']
farith['infil2'] = pars['model_map']
farith['outfil'] = 'diffMap.fits'
farith['ops'] = 'SUB'

pars['diff_map'] = farith['outfil']
pars.write()

if debug:
    print farith.command()
else:
    farith.run()
