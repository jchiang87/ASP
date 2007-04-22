"""
@brief Combine gtexpmap submaps for DRP monitoring.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from combineExpMaps import combineExpMaps

from drpRoiSetup import rootpath, pars, rois

debug = False

id = int(os.environ['ROI_ID']) - 1
name = rois[id].name

os.chdir(name)

if debug:
    print "running combineExMaps"
else:
    combineExpMaps(outfile=pars['expMap'])

os.system('chmod 777 *')
