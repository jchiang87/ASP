"""
@brief Compute the file information for downlink files.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import pyfits

def getObsTimes(vars):
    ft1File = os.path.join(vars["downlinkDir"], vars["downlinkFile"])
    events = pyfits.open(ft1File)["EVENTS"]
    return events.header["TSTART"], events.header["TSTOP"]

variables = {}
variables["downlinkDir"] = "/nfs/farm/g/glast/u33/jchiang/DC2/Downlinks"
variables["downlinkFile"] = "downlink_0000.fits"

tstart, tstop = getObsTimes(variables)
variables["tstart"] = "%i" % tstart
variables["tstop"] = "%i" % tstop

print variables

summary = open(os.environ["PIPELINE_SUMMARY"], 'a')
for item in variables:
    summary.write("pipeline.%s : %s\n" % (item, variables[item]))
summary.close()
