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

#_L1DataPath = '/nfs/farm/g/glast/u33/jchiang/ASP/testdata/downlinks'
#_ft2File = '/nfs/farm/g/glast/u33/jchiang/ASP/testdata/eg_diffuse_scData_0000.fits'
#_startTime = 0
_L1DataPath = '/nfs/farm/g/glast/u33/jchiang/DC2/Downlinks'
_ft2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'
_startTime = 220838400

debug = False

output_dir = os.environ['output_dir']
os.chdir(output_dir)

start_time = float(os.environ['start_time'])
stop_time = float(os.environ['stop_time'])

gtselect = GtApp('gtselect')

ft1, ft2 = getL1Data(start_time, stop_time, l1DataPath=_L1DataPath,
                     ft2File=_ft2File, startTime=_startTime)
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
#pars = Parfile(os.path.join(os.environ['PYASPROOT'], 'data', parfile_basename))
pars = Parfile(parfile_basename)
pars['ft1file'] = gtselect['outfile']
pars['ft2file'] = ft2[0]    # need to generalize this for multiple FT2 files
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars['RoI_file'] = os.environ['RoI_file']
pars.write()

os.system('chmod 777 *')
