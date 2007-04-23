"""
@brief Create a TS map using gttsmap.

@author J. Chiang <jchiang@slac.stanford.edu>

"""
#
# $Header$
#
import os
from GtApp import GtApp

os.chdir(os.environ['OUTPUTDIR'])

gttsmap = GtApp('gttsmap')

# Use par file written by refinePosition.py

gttsmap.run()
