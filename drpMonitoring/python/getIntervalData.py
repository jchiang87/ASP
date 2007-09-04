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
from getL1Data import getL1Data
from ft1merge import ft1merge
from parfile_parser import Parfile

debug = False

output_dir = os.environ['output_dir']

ft1_list = 'Ft1FileList'
shutil.copy(ft1_list, os.path.join(output_dir, ft1_list))
os.chdir(output_dir)

start_time = float(os.environ['TSTART'])
stop_time = float(os.environ['TSTOP'])

gtselect = GtApp('gtselect')

ft1, ft2 = getL1Data(start_time, stop_time)

ft1 = []
for line in open(ft1_list):
    ft1.append(line.strip())

print "Using downlink files: ", ft1

ft1Merged = 'FT1_merged.fits'
ft1merge(ft1, ft1Merged)

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
pars['ft2file'] = ft2[0]    # need to generalize this for multiple FT2 files
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars['RoI_file'] = os.environ['RoI_file']
pars.write()

os.system('chmod 777 *')
