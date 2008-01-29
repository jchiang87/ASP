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

class FileStager(object):
    def __init__(self, stagingArea, messageLevel="CRITICAL"):
        level = eval("logging." + messageLevel)
        log.setLevel(level)
        self.stager = GPL.stageFiles.StageSet(stagingArea)
    def in_out(self, infile, outfile):
        if infile == outfile:
            raise RuntimeError, "Cannot have identical input & output filenames"
        return self.input(infile), self.output(outfile)
    def input(self, infile):
        return self.stager.stageIn(infile)
    def output(self, outfile):
        return self.stager.stageOut(outfile)
    def __del__(self):
        self.stager.finish("alldone")
