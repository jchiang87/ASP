"""
@brief Utilities and variables for creating Pipeline-II streams for
various ASP tasks

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import time

try:
    _pipelineServer = os.environ['PIPELINESERVER']
except KeyError:
    _pipelineServer = 'PROD'
    os.environ['PIPELINESERVER'] = _pipelineServer

#print "ASP/PipelineCommand, using:"
#print "PIPELINESERVER = %s" % _pipelineServer
#print 

def resolve_nfs_path(path):
    tokens = path.split(":")
    for i in range(len(tokens)):
        if tokens[i].find('g.glast.'):
            tokens[i] = os.path.join('/nfs/farm/g/glast', 
                                     tokens[i].split('g.glast.')[-1])
    return ":".join(tokens)

class PipelineError(EnvironmentError):
    "Pipeline stream creation failed"

class PipelineCommand(object):
    def __init__(self, taskname, args, stream=None):
        "Abstraction for a Pipeline-II command."
        if stream is None:
#            stream = self.streamNumber()
            stream = -1
        executable = '/afs/slac/g/glast/ground/bin/pipeline'
        self.command = ('%s -m %s createStream -S %s -D "%s" %s'
                        % (executable, _pipelineServer, stream, 
                           self._argString(args), taskname))
    def run(self, debug=False):
        print self.command + "\n"
        if not debug:
            rc = os.system(self.command)
        else:
            rc = 0
        if rc != 0:
            raise PipelineError, ("pipeline return code: %i" % rc)
    def streamNumber(self):
        """Provide a unique stream number for the pipeline based on the
        current date and time.
        """
        time.sleep(1)     # to ensure unique stream numbers
        return "%i%02i%02i%02i%02i" % time.localtime()[1:6]
    def _argString(self, argDict):
        """Construct the argument stream for a pipeline task.  Entries in
        the default dictionary can be over-ridden by key-value pairs in
        the argDict.
        """
        defaultDict = {'PIPELINESERVER' : _pipelineServer}
        defaultDict.update(argDict)
        arg_string = ""
        for item in defaultDict:
            arg_string += '%s=%s,' % (item, defaultDict[item])
        return arg_string.strip(',')
