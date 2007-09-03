"""
@brief Run gtexpmap for GRB afterglow analysis, using specified submaps
to be run in parallel.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

#import os
#from exposureSubMap import exposureSubMap
#
#exposureSubMap(os.environ['OUTPUTDIR'], debug=False)

import os
from GtApp import GtApp

os.chdir(os.environ['OUTPUTDIR'])

gtexpmap = GtApp('gtexpmap', 'Likelihood')
gtexpmap.run()

os.system('chmod 777 *')

