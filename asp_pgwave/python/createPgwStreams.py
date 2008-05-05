"""
@brief Create streams for DRP monitoring task.

@author J. Chiang
"""
#
# $Header$
#

import os
from read_data import read_data
from PipelineCommand import PipelineCommand, _outputDir, _asp_path

# import this to ensure it is available for the various streams
import pyASP

_version = os.path.split(os.environ['PGWAVEROOT'])[-1]
_pgwRoot = os.path.join(_asp_path, 'ASP', 'pgwave', _version)
_catdir = '/nfs/farm/g/glast/u33/tosti/october/catdir'

_startTime = 220838400.   # for DC2 data

def pgwStreams(downl=1, output_dir=_outputDir, startTime=_startTime, 
            debug=False, logicalPath=None):
    start_time = 252737700
    #TSTOP=252743070#(downl-1)*1.04e4 + startTime
    stop_time =252743070 # start_time +1.04e4 
    os.chdir(output_dir)
    args = {'OUTPUTDIR' : output_dir,
            'TSTART' : start_time,
            'TSTOP' : stop_time,
            'CATDIR': _catdir, 
            'PGWAVEROOT' : _pgwRoot,
            'logicalPath' : '/DC2/OktoberTest'}
    if logicalPath is not None:
            args['logicalPath'] = logicalPath
    command = PipelineCommand('PGWave', args)
    command.run(debug=debug)

if __name__ == '__main__':
    pgwStreams(debug=True)
