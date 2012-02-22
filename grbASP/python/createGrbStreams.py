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
import BayesianBlocks

_grbAspRoot = resolve_nfs_path(os.environ['INST_DIR'])

def blindSearchStreams(downlinks=None, grbroot_dir=None, folder=None,
                       debug=False, streamId=None, 
                       datacatalog_imp="datacatalog",
                       outputFolder=None):
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
                'datacatalog_imp' : datacatalog_imp}
        if folder is not None:
            args['folder'] = folder
        if outputFolder is not None:
            args['outputFolder'] = outputFolder
        command = PipelineCommand('GRB_blind_search', args, stream=streamId)
        command.run(debug=debug)

def refinementStreams(tstart, tstop, folder=None, 
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
                'datacatalog_imp' : datacatalog_imp}
        if folder is not None:
            args['folder'] = folder
        command = PipelineCommand('GRB_refinement', args, stream=streamId)
        command.run(debug=debug)

def afterglowStreams(parfiles=None, output_dir=None, debug=False,
                     folder=None, streamId=None, 
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
                'datacatalog_imp' : datacatalog_imp}
        if folder is not None:
            args['folder'] = folder
        command = PipelineCommand('GRB_afterglow', args, stream=streamId)
        command.run(debug=debug)

if __name__ == '__main__':
    blindSearchStreams('downlink_file', 'grbroot_dir', debug=True)
    refinementStreams((1391,), debug=True)
    afterglowStreams('GRB_parfile', debug=True)
