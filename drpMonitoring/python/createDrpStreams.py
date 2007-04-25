"""
@brief Create streams for DRP monitoring task.

@author J. Chiang
"""
#
# $Header$
#

import os
from read_data import read_data
from PipelineCommand import PipelineCommand, _outputDir

# import this to ensure it is available for the various streams
import pyASP

_startTime = 220838400.   # for DC2 data
#_startTime = 0.            # for testdata

_sourceModel = os.path.join(os.environ['DRPMONITORINGROOT'], 'data',
                            'DRP_SourceModel.xml')

def drpStreams(daynum=1, output_dir=_outputDir, RoI_file='rois.txt',
               sourceModel=_sourceModel, startTime=_startTime, debug=False,
               num_RoIs=None):
    start_time = (daynum-1)*8.64e4 + startTime
    stop_time = start_time + 8.64e4
    os.chdir(output_dir)
    foo = read_data(RoI_file)
    if num_RoIs is None:
        num_RoIs = len(foo[0])
    args = {'output_dir' : output_dir,
            'start_time' : start_time,
            'stop_time' : stop_time,
            'RoI_file' : RoI_file,
            'num_RoIs' : num_RoIs,
            'sourceModelFile' : sourceModel}
    command = PipelineCommand('DRP_monitoring', args)
    command.run(debug=debug)

if __name__ == '__main__':
    drpStreams(debug=True)
