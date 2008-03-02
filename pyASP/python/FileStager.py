"""
@brief Encapsulate GPL package imports and file staging code.  Allow
users to set logging message level.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

#
# Silence the start up message.
#
os.environ["GPL2_DEBUGLVL"] = "INFO"

import GPLinit    # There never is one without the other....
import GPL

import logging
log = logging.getLogger("gplLong")

class FileStagerError(IOError):
    "Unknown error occurred in GPL.stageFiles.finish(...)"

class FileStager(object):
    def __init__(self, stageName, messageLevel="CRITICAL", stageArea=None,
                 cleanup=True):
        level = eval("logging." + messageLevel)
        log.setLevel(level)
        self.stager = GPL.stageFiles.StageSet(stageName, stageArea=stageArea)
        self.cleanup = cleanup
    def in_out(self, infile, outfile):
        if infile == outfile:
            raise RuntimeError, "Cannot have identical input & output filenames"
        return self.input(infile), self.output(outfile)
    def input(self, infileArg):
        # Strip possible leading "+" in case the file hasn't been scanned.
        # GPL.stageFiles code does not throw an exception if it is asked to
        # stage a file that doesn't exist, yet it will return a valid path
        # for the staged file.
        infile = infileArg.strip('+')
        return self.stager.stageIn(infile)
    def output(self, outfile):
        return self.stager.stageOut(outfile)
    def __del__(self):
        if not self.cleanup:
            return
        rc = self.stager.finish("alldone")
        if rc != 0:
            message = "Unknown error occurred in GPL.stageFiles.finish(...)"
            raise FileStagerError, message
    def infiles(self, infiles):
        filelist = []
        for item in infiles:
            filelist.append(self.input(item))
        return filelist
