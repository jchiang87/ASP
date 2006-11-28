"""
@brief Extract FT1 data for a specified time range given by start_time and
stop_time environment variables.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
from getL1Data import getL1Data
from ft1merge import ft1merge
from parfile_parser import Parfile

debug = False

os.chdir(os.environ['root_output_dir'])

start_time = float(os.environ['start_time'])
stop_time = float(os.environ['stop_time'])

gtselect = GtApp('gtselect')

ft1, ft2 = getL1Data(start_time, stop_time)

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
pars = Parfile(os.path.join(os.environ['PYASPROOT'], 'data', parfile_basename))
pars['ft1file'] = gtselect['outfile']
pars['ft2file'] = ft2    # need to generalize this for multiple FT2 files
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars['RoI_file'] = os.environ['RoI_file']
pars.write(parfile_basename)

os.system('chmod 666 *')