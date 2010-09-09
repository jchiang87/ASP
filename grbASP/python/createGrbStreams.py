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
from PipelineCommand import PipelineCommand, resolve_nfs_path

# import these to ensure they are available for the various streams
import grbASP
import pyIrfLoader
import BayesBlocks

#_version = os.path.split(os.environ['GRBASPROOT'])[-1]
try:
    _grbAspRoot = resolve_nfs_path(os.environ['GRBASPROOT'])
except KeyError:   # probably using an SCons build
    _grbAspRoot = resolve_nfs_path(os.environ['INST_DIR'])

def blindSearchStreams(downlinks=None, grbroot_dir=None, logicalPath=None,
                       debug=False, streamId=None, 
                       datacatalog_imp="datacatalog",
                       outputFolder=None,
                       SCons=False):
    if downlinks is None:
        raise ValueError, "No downlink IDs specified"
    if grbroot_dir is None:
        grbroot_dir = os.path.abspath(os.environ['GRBROOTDIR'])
    if isinstance(downlinks, int):
        downlinks = (downlinks, )
    for downlink in downlinks:
        args = {'DownlinkId' : downlink,
                'GRBROOTDIR' : grbroot_dir,
                'GRBASPROOT' : _grbAspRoot,
                'logicalPath' : '/DC2/Downlinks',
                'datacatalog_imp' : datacatalog_imp}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        if outputFolder is not None:
            args['outputFolder'] = outputFolder
        command = PipelineCommand('GRB_blind_search', args, stream=streamId)
#        if not SCons:
#            command = PipelineCommand('GRB_blind_search', args, stream=streamId)
#        else:
#            command = PipelineCommand('GRB_blind_search-SCons', args,
#                                      stream=streamId)
        command.run(debug=debug)

def refinementStreams(tstart, tstop, logicalPath=None,
                      grb_ids=(), output_dir=None, debug=False,
                      streamId=None, 
                      datacatalog_imp="datacatalog"):
    for grb_id in grb_ids:
        args = {'GCN_NOTICE' : 'None',
                'GRB_ID' : grb_id, 
                'OUTPUTDIR' : output_dir,
                'GRBASPROOT' : _grbAspRoot,
                'TSTART' : tstart,
                'TSTOP' : tstop,
                'logicalPath' : '/DC2/Downlinks',
                'datacatalog_imp' : datacatalog_imp}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        command = PipelineCommand('GRB_refinement', args, stream=streamId)
        command.run(debug=debug)

def afterglowStreams(parfiles=None, output_dir=None, debug=False,
                     logicalPath=None, streamId=None,
                     datacatalog_imp="datacatalog"):
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
                'GRBPARS' : parfile,
                'OUTPUTDIR' : output_dir,
                'GRBASPROOT' : _grbAspRoot,
                'logicalPath' : '/DC2/Downlinks',
                'datacatalog_imp' : datacatalog_imp}
        if logicalPath is not None:
            args['logicalPath'] = logicalPath
        command = PipelineCommand('GRB_afterglow', args, stream=streamId)
        command.run(debug=debug)

if __name__ == '__main__':
    blindSearchStreams('downlink_file', 'grbroot_dir', debug=True)
    refinementStreams((1391,), debug=True)
    afterglowStreams('GRB_parfile', debug=True)
