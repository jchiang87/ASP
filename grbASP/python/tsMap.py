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
from refinePosition import absFilePath

os.chdir(os.environ['OUTPUTDIR'])

gttsmap = GtApp('gttsmap', 'Likelihood')

# Use par file written by refinePosition.py

gttsmap.run()

grb_id = int(os.environ['GRB_ID'])
dbAccess.updateGrb(grb_id, TS_MAP="'%s'" % absFilePath(gttsmap['outfile']))

# create plots

command = ("/afs/slac/g/glast/ground/grbMonitoring/bin/makeAllPlots . png %i"
           % grb_id)
os.system(command)
