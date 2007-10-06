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
from parfile_parser import Parfile
from PipelineCommand import PipelineCommand, _outputDir, _asp_path

# import these to ensure they are available for the various streams
import grbASP
import pyIrfLoader
import BayesBlocks

_version = os.path.split(os.environ['GRBASPROOT'])[-1]
_grbAspRoot = os.path.join(_asp_path, 'ASP', 'grbASP', _version)

def blindSearchStreams(downlinks=None, grbroot_dir=None, logicalPath=None,
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
                'GRBASPROOT' : _grbAspRoot,
                'logicalPath' : '/DC2/Downlinks'}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        command = PipelineCommand('GRB_blind_search', args)
        command.run(debug=debug)

#def refinementStreams(notices=None, output_dir=_outputDir, debug=False):
#    os.chdir(output_dir)
#    if notices is None:
#        notices = glob.glob('GRB*_Notice.txt')
#    if isinstance(notices, str):
#        grb_ids = (notices, )
#    for notice in notices:
#        args = {'GCN_NOTICE' : notice,
#                'output_dir' : output_dir,
#                'GRBASPROOT' : _grbAspRoot}
#        command = PipelineCommand('GRB_refinement', args)
#        command.run(debug=debug)

def refinementStreams(tstart, tstop, logicalPath=None,
                      grb_ids=(), output_dir=_outputDir, debug=False):
    os.chdir(output_dir)
    for grb_id in grb_ids:
        args = {'GCN_NOTICE' : 'None',
                'GRB_ID' : grb_id, 
                'output_dir' : output_dir,
                'GRBASPROOT' : _grbAspRoot,
                'TSTART' : tstart,
                'TSTOP' : tstop,
                'logicalPath' : '/DC2/Downlinks'}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        command = PipelineCommand('GRB_refinement', args)
        command.run(debug=debug)

def afterglowStreams(parfiles=None, output_dir=_outputDir, debug=False,
                     logicalPath=None):
    os.chdir(output_dir)
    if parfiles is None:
        parfiles = glob.glob('GRB*_pars.txt')
    if isinstance(parfiles, str):
        parfiles = (parfiles, )
    from GrbAspConfig import grbAspConfig
    for parfile in parfiles:
        params = Parfile(parfile)
        tstart = params['tstop']
        config = grbAspConfig.find(tstart)
        tstop = tstart + config.AGTIMESCALE
        args = {'TSTART' : tstart,
                'TSTOP' : tstop,
                'GRB_parfile' : parfile,
                'output_dir' : output_dir,
                'GRBASPROOT' : _grbAspRoot,
                'logicalPath' : '/DC2/Downlinks'}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        command = PipelineCommand('GRB_afterglow', args)
        command.run(debug=debug)

if __name__ == '__main__':
    blindSearchStreams('downlink_file', 'grbroot_dir', debug=True)
    refinementStreams((1391,), debug=True)
    afterglowStreams('GRB_parfile', debug=True)
