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

def pyASProot():
    version = os.environ['PYASPROOT'].split(os.path.sep)[-1]
    return os.path.join('/nfs/farm/g/glast/u33/jchiang/ASP/pyASP', version)

_pyASProot = pyASProot()
_outputDir = os.environ['OUTPUTDIR']

print "Using:\n\nPYASPROOT = %s\nOUTPUTDIR = %s\n" % (_pyASProot, _outputDir)

def argString(argDict):
    arg_string = (','.join(('output_dir=%s', 'PYASPROOT=%s'))
               % (_outputDir, _pyASProot))
    for item in argDict:
        arg_string += ',%s=%s' % (item, argDict[item])
    return arg_string    

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
    os.chdir(_outputDir)
    if downlinks is None:
        raise ValueError, "No downlink files specified"
    if isinstance(downlinks, str):
        downlinks = (downlinks, )
    for downlink in downlinks:
        args = argString({'Downlink_file': downlink})
        command = pipelineCommand('GRB_blind_search', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

def refinementStreams(notices=None):
    os.chdir(_outputDir)
    if notices is None:
        notices = glob.glob('GRB*_Notice.txt')
    if isinstance(notices, str):
        notices = (notices, )
    for notice in notices:
        args = argString({'GBM_Notice': notice})
        command = pipelineCommand('GBM_refinement', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

def afterglowStreams(parfiles=None):
    os.chdir(_outputDir)
    if parfiles is None:
        parfiles = glob.glob('GRB*_pars.txt')
    if isinstance(parfiles, str):
        parfiles = (parfiles, )
    for parfile in parfiles:
        args = argString({'GRB_parfile': parfile})
        command = pipelineCommand('GRB_afterglow', args)
        print command
        rc = os.system(command)
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)

if __name__ == '__main__':
    pass
#    blindSearchStreams('foo')
#    refinementStreams('bar')
#    afterglowStreams('foobar')
