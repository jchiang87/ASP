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
from drpRoiSetup import currentRoi

roi = currentRoi()
outputDir = roi.name

exposureSubMap(outputDir, debug=False)
