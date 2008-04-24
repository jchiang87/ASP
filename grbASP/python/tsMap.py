"""
@brief Create a TS map using gttsmap.

@author J. Chiang <jchiang@slac.stanford.edu>

"""
#
# $Header$
#
import os
from GtApp import GtApp
import dbAccess
from refinePosition import absFilePath, likelyUL
import pipeline

os.chdir(os.environ['OUTPUTDIR'])
grb_id = int(os.environ['GRB_ID'])

if likelyUL(grb_id):
    print "Likely upper limit candidate.  Skipping TS map calculation."
    pipeline.setVariable('LIKELY_UPPER_LIMIT', 'true')
else:
    pipeline.setVariable('LIKELY_UPPER_LIMIT', 'false')
    gttsmap = GtApp('gttsmap', 'Likelihood')
    gttsmap.run() # Use par file written by refinePosition.py
    dbAccess.updateGrb(grb_id, TS_MAP="'%s'" % absFilePath(gttsmap['outfile']))

