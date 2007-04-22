"""
@brief Run gtexpmap for DRP source monitoring, using specified submaps
to be run in parallel.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from exposureSubMap import exposureSubMap
from drpRoiSetup import rootpath, pars, rois

id = int(os.environ['ROI_ID']) - 1
outputDir = rois[id].name

exposureSubMap(outputDir, debug=False)
