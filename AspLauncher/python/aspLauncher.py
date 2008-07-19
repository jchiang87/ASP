"""
@file aspLauncher.py

@brief This script queries the TIMEINTERVALS db table and calculates
the next set of intervals for which the associated ASP tasks are
launched.  The wrapped version of this script is intended to be
launched as a subprocess of L1Proc.

Two environment variables need to be provided:

nDownlink = Data delivery ID of the current L1Proc instance
folder = Logical folder in the dataCatalog that contains the FT1/2 data

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, sys
from createGrbStreams import blindSearchStreams
from intervalAccess import unhandledIntervals
from PipelineCommand import PipelineCommand, resolve_nfs_path, PipelineError

_aspLauncherRoot = resolve_nfs_path(os.environ['ASPLAUNCHERROOT'])

#
# Standard output directory for ASP results.  This is a symlink to
# a location on nfs.
#
_output_dir = '/afs/slac/g/glast/ground/links/data/ASP/Results'

aspOutput = lambda x : os.path.join(_output_dir, x)

try:
   os.environ['folder'], os.environ['nDownlink']
except KeyError:
   print "The following env vars must be set:"
   print "folder = <datacatalog folder containing FT1/2 data>"
   print "nDownlink = <metadata ID number for the desired data delivery>"

try:
   debug = eval(os.environ['ASP_LAUNCHER_DEBUG'])
except KeyError:
   debug = False

print "AspLauncher script, using: "
print "DataCatalog folder =", os.environ['folder']
print "Downlink ID =", os.environ['nDownlink']
print "debug mode =", debug
print

duplicateStreamException = False

nDownlink = int(os.environ['nDownlink'])

try:
   blindSearchStreams(downlinks=(nDownlink,),
                      logicalPath=os.environ['folder'],
                      grbroot_dir=aspOutput('GRB'),
                      streamId=nDownlink, 
                      datacatalog_imp="datacatalog",
                      debug=debug)
except PipelineError, message:
   if message.message("DuplicateStreamException"):
      duplicateStreamException = True
   else:
      raise

args = {'folder' : os.environ['folder'],
        'nDownlink' : nDownlink,
        'PIPELINESERVER' : os.environ['PIPELINESERVER'],
        'ASPLAUNCHERROOT' : _aspLauncherRoot,
        'datacatalog_imp' : 'datacatalog'}
inserter = PipelineCommand('AspInsertIntervals', args)
inserter.run(debug=debug)

unhandled = unhandledIntervals()
for frequency in unhandled:
   for interval in unhandled[frequency]:
      args = {'folder' : os.environ['folder'],
              'interval' : interval.interval,
              'frequency' : frequency,
              'nMetStart' : interval.tstart,
              'nMetStop' : interval.tstop,
              'GRBOUTPUTDIR' : aspOutput('GRB'),
              'DRPOUTPUTDIR' : aspOutput('DRP'),
              'PGWAVEOUTPUTDIR' : aspOutput('PGWAVE'),
              'PIPELINESERVER' : os.environ['PIPELINESERVER'],
              'ASPLAUNCHERROOT' : _aspLauncherRoot,
              'datacatalog_imp' : 'datacatalog'}

      for item in args:
         print item, args[item]
      print "\n*******************\n"

      launcher = PipelineCommand('AspLauncher', args)
      launcher.run(debug=debug)

if duplicateStreamException:
   sys.exit(160)
