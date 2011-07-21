"""
@brief Create streams for DRP monitoring task.

@author J. Chiang
"""
#
# $Header$
#

import os, sys
from read_data import read_data
from PipelineCommand import PipelineCommand, _outputDir, _asp_path

# import this to ensure it is available for the various streams
import pyASP

_version = os.path.split(os.environ['DRPMONITORINGROOT'])[-1]
_drpRoot = os.path.join(_asp_path, 'ASP', 'drpMonitoring', _version)

_startTime = 220838400.   # for DC2 data

def drpStreams(daynum=1, output_dir=_outputDir, startTime=_startTime, 
               num_RoIs=1, folder=None, debug=False):
    start_time = (daynum-1)*8.64e4 + startTime
    stop_time = start_time + 8.64e4
    os.chdir(output_dir)
    args = {'OUTPUTDIR' : output_dir,
            'interval' : daynum,
            'TSTART' : start_time,
            'TSTOP' : stop_time,
            'num_RoIs' : num_RoIs,
            'DRPMONITORINGROOT' : _drpRoot}
    if folder is not None:
        args['folder'] = folder
    command = PipelineCommand('DRP_monitoring', args)
    command.run(debug=debug)

if __name__ == '__main__':
    drpStreams(debug=True)
