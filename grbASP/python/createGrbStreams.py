"""
@brief Create streams for various top level GRB tasks.

@author J. Chiang
"""
#
# $Header$
#

import os
import glob
import time
from PipelineCommand import PipelineCommand, _outputDir

# import these to ensure they are available for the various streams
import grbASP
import pyIrfLoader
import BayesBlocks

_grbAspRoot = '/nfs/farm/g/glast/u33/jchiang/ASP/ASP/grbASP/v0'

def blindSearchStreams(downlinks=None, grbroot_dir=None,
                       output_dir=_outputDir, debug=False):
    os.chdir(output_dir)
    if downlinks is None:
        raise ValueError, "No downlink files specified"
    if grbroot_dir is None:
        grbroot_dir = os.path.abspath(os.environ['GRBROOTDIR'])
    if isinstance(downlinks, str):
        downlinks = (downlinks, )
    for downlink in downlinks:
        args = {'Downlink_file' : downlink,
                'GRBROOTDIR' : grbroot_dir,
                'GRBASPROOT' : _grbAspRoot}
        command = PipelineCommand('GRB_blind_search', args)
        command.run(debug=debug)

def refinementStreams(notices=None, output_dir=_outputDir, debug=False):
    os.chdir(output_dir)
    if notices is None:
        notices = glob.glob('GRB*_Notice.txt')
    if isinstance(notices, str):
        notices = (notices, )
    for notice in notices:
        args = {'GBM_Notice' : notice,
                'output_dir' : output_dir,
                'GRBASPROOT' : _grbAspRoot}
        command = PipelineCommand('GRB_refinement', args)
        command.run(debug=debug)

def afterglowStreams(parfiles=None, output_dir=_outputDir, debug=False):
    os.chdir(output_dir)
    if parfiles is None:
        parfiles = glob.glob('GRB*_pars.txt')
    if isinstance(parfiles, str):
        parfiles = (parfiles, )
    for parfile in parfiles:
        args = {'GRB_parfile' : parfile,
                'output_dir' : output_dir,
                'GRBASPROOT' : _grbAspRoot}
        command = PipelineCommand('GRB_afterglow', args)
        command.run(debug=debug)

if __name__ == '__main__':
    blindSearchStreams('downlink_file', 'grbroot_dir', debug=True)
    refinementStreams('GBM_Notice', debug=True)
    afterglowStreams('GRB_parfile', debug=True)
