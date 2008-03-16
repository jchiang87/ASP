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

_pyASProot = '/nfs/farm/g/glast/u33/jchiang/ASP/pyASP/v0r1'

def streamNumber():
    time.sleep(1)     # to ensure unique stream numbers
    return "%i%02i%02i%02i%02i" % time.localtime()[1:6]

def pipelineCommand(taskname, args, stream=None):
    command = '~glast/pipeline-II/pipeline createStream %s %s "%s"'
    if stream is None:
        stream = streamNumber()
    return command % (taskname, stream, args)

class PipelineError(EnvironmentError):
    "Pipeline stream creation failed"

def blindSearchStreams(downlinks=None):
    os.chdir(os.environ['OUTPUTDIR'])
    if downlinks is None:
        raise ValueError, "No downlink files specified"
    if isinstance(downlinks, str):
        downlinks = (downlinks, )
    for downlink in downlinks:
        args = (','.join(('Downlink_file=%s',
                          'output_dir=%s',
                          'PYASPROOT=%s'))
                % (downlink, os.environ['OUTPUTDIR'], _pyASProot))
        command = pipelineCommand('GRB_blind_search', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

def refinementStreams(notices=None):
    os.chdir(os.environ['OUTPUTDIR'])
    if notices is None:
        notices = glob.glob('GRB*_Notice.txt')
    if isinstance(notices, str):
        notices = (notices, )

    for notice in notices:
        args = (','.join(("GBM_Notice=%s",
                          "output_dir=%s",
                          "PYASPROOT=%s"))
                % (notice, os.environ['OUTPUTDIR'], _pyASProot))
        command = pipelineCommand('GBM_refinement', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

def afterglowStreams(parfiles=None):
    os.chdir(os.environ['OUTPUTDIR'])
    if parfiles is None:
        parfiles = glob.glob('GRB*_pars.txt')
    if isinstance(parfiles, str):
        parfiles = (parfiles, )

    for parfile in parfiles:
        args = (','.join(("output_dir=%s",
                          "GRB_parfile=%s",
                          "PYASPROOT=%s"))
                % (os.environ['OUTPUTDIR'], parfile, _pyASProot))
        command = pipelineCommand('GRB_afterglow', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

#if __name__ == '__main__':
#    blindSearchStreams('foo')
#    refinementStreams('bar')
#    afterglowStreams('foobar')
