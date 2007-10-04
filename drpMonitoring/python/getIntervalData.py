"""
@brief Extract FT1 data for a specified time range given by TSTART and
TSTOP environment variables.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, shutil
from GtApp import GtApp
#from getL1Data import getL1Data
from getFitsData import getFitsData
from ft1merge import ft1merge
from parfile_parser import Parfile
import drpDbAccess

debug = False

ft1, ft2 = getFitsData()

output_dir = os.environ['OUTPUTDIR']
os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

gtselect = GtApp('gtselect')

print "Using downlink files: ", ft1

ft1Merged = 'FT1_merged.fits'
ft1merge(ft1, ft1Merged)

fmerge = GtApp('fmerge')
fmerge['infiles'] = '@Ft2FileList'
fmerge['outfile'] = 'FT2_merged.fits'
fmerge['clobber'] = 'yes'
fmerge['columns'] = '" "'
fmerge['mextname'] = '" "'
fmerge['lastkey'] = '" "'
fmerge.run()

gtselect['infile'] = ft1Merged
gtselect['outfile'] = 'time_filtered_events.fits'
gtselect['tmin'] = start_time
gtselect['tmax'] = stop_time
gtselect['rad'] = 180.

if debug:
    print gtselect.command()
else:
    gtselect.run()

parfile_basename = 'drp_pars.txt'
pars = Parfile(parfile_basename)
pars['ft1file'] = gtselect['outfile']
pars['ft2file'] = fmerge['outfile']
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars.write()

drpDbAccess.readRois()

os.system('chmod 777 *')
