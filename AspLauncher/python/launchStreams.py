"""
@file launchStreams.py

@brief For each downlink emitted by L1Proc, check for the availability
of L1 data for the next scheduled instance of each task and launch
each one if the required data are available.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from checkLevelOneFiles import providesCoverage
from createGrbStreams import blindSearchStreams
from createDrpStreams import launch_drp
from createPGwaveStream import launch_pgwvae

def get_interval(freq):
    return (int(os.environ[freq + '_interval']), 
            int(os.environ[freq + '_nMetStart']), 
            int(os.environ[freq + '_nMetStop']))

min_frac = float(os.environ['minimum_coverage'])
folder = os.environ['folder']

nDownlink = int(os.environ['nDownlink'])
blindSearchStreams(downlinks=(nDownlink,), logicalPath=folder, 
                   output_dir=os.environ['GRBOUTPUTDIR'])

interval, tstart, tstop = get_interval('SixHour')
if providesCoverage(tstart, tstop, min_frac, 
                    'Ft1FileList_6hr', 'Ft2FileList_6hr'):
    launch_pgwave(tstart, tstop)

interval, tstart, tstop = get_interval('Daily')
if providesCoverage(tstart, tstop, min_frac, 
                    'Ft1FileList_day', 'Ft2FileList_day'):
    launch_drp(interval, tstart, tstop, folder, 
               output_dir=os.environ['DRPOUTPUTDIR'])

interval, tstart, tstop = get_interval('Weekly')
if providesCoverage(tstart, tstop, min_frac, 
                    'Ft1FileList_week', 'Ft2FileList_week'):
    launch_drp(interval, tstart, tstop, folder, 
               output_dir=os.environ['DRPOUTPUTDIR'])
