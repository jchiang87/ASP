"""
@brief Combine gtexpmap submaps for DRP monitoring.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from combineExpMaps import combineExpMaps

from drpRoiSetup import pars, currentRoi

debug = False

roi = currentRoi()
os.chdir(roi.name)

if debug:
    print "running combineExMaps"
else:
    combineExpMaps(outfile=pars['expMap'])

os.system('chmod 777 *')
