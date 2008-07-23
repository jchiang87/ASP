"""
@file launchRspStreams.py

@brief This will launch the RspPulsarDb stream.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from PipelineCommand import PipelineCommand, resolve_nfs_path

_rsppulsarroot = resolve_nfs_path(os.environ['RSPPULSARROOT'])
_rsppulsarroot.rstrip('/')
_rsppulsarroot += '/'
_rsp_path = _rsppulsarroot.split('RSP')[0]

def launch_RspPulsar(frequency, tstart, tstop, folder, debug=False):
    args = {'RSPPULSARROOT' : _rsppulsarroot,
            'logicalPath' : folder,
            'OUTPUTDIR' : '/nfs/farm/g/glast/u20/RSP/RspPulsar/v0r0/data/',
            'TSTART' : tstart,
            'TSTOP' : tstop,
            'RSP_PATH' : _rsp_path,
            'PULSAR_LIST' : 'D4_test.txt',
            'PULSAR_DB' : 'D4_new.fits',
            'CATALOG' : 'toto.fits',
            'FREQUENCY' : 'pulsar_' +frequency}
    command = PipelineCommand('RspPulsarDB', args)
    command.run(debug=debug)
