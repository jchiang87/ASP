"""
@file aspLauncher.py

@brief This script queries the TIMEINTERVALS db table and calculates the
next set of intervals for which the associated ASP tasks are launched.
This is intended to be launched as a subprocess of L1Proc.

Two environment variables need to be provided:

nDownlink = Downlink ID of the current L1Proc instance
folder = Logical folder in the dataCatalog that contains the FT1/2 data

The bash wrapper script requires two addtional environment variables:

ST_INST = path to ST installation, e.g.,
       /nfs/farm/g/glast/u30/builds/rh9_gcc32/ScienceTools/ScienceTools-v9r5
ASP_PATH = path to ASP installation, e.g., /afs/slac/g/glast/ground/ASP/prod

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from createGrbStreams import blindSearchStreams
import databaseAccess as dbAccess

def find_frequencies():
   sql = "select FREQUENCY from FREQUENCIES"
   def getFrequencies(cursor):
       freqs = []
       for entry in cursor:
           freqs.append(entry[0])
       return freqs
   return dbAccess.apply(sql, getFrequencies)

class TimeInterval(object):
   def __init__(self, entry):
      self.interval = entry[0]
      self.frequency = entry[1]
      self.tstart = entry[2]
      self.tstop = entry[3]
      self.is_processed = entry[4]

def find_intervals():
   """Find unhandled intervals"""
   sql = ("SELECT * from TIMEINTERVALS where IS_PROCESSED=0 "
          + "order by interval_number asc")
   frequencies = find_frequencies()
   unhandled = {}
   for freq in frequencies:
      unhandled[freq] = []
   def findUnhandled(cursor, unhandled=unhandled):
      for entry in cursor:
         timeInterval = TimeInterval(entry)
         unhandled[timeInterval.frequency].append(timeInterval)
      return unhandled
   try:
      return dbAccess.apply(sql, findUnhandled)
   except dbAccess.cx_Oracle.DatabaseError, message:
      print message
      print sql

if __name__ == '__main__':
    _asp_path = os.environ['ASP_PATH']
    _version = os.path.split(os.environ['ASPLAUNCHERROOT'])[-1]
    _aspLauncherRoot = os.path.join(_asp_path, 'ASP', 'AspLauncher', _version)

    from PipelineCommand import PipelineCommand

    #
    # Standard output directory for ASP results.  Will this be
    # replaced by a symlink as proposed?
    #
    _output_dir = '/nfs/farm/g/glast/u33/ASP/OpsSim2Dev'

    aspOutput = lambda x : os.path.join(_output_dir, x)

    try:
       os.environ['folder'], os.environ['nDownlink']
    except KeyError:
       os.environ['folder'] = '/Data/OpsSim2/Level1'
       os.environ['nDownlink'] = '80302002'

    print "Using "
    print "DataCatalog folder =", os.environ['folder']
    print "Downlink ID =", os.environ['nDownlink']

    nDownlink = int(os.environ['nDownlink'])
    blindSearchStreams(downlinks=(nDownlink,),
                       logicalPath=os.environ['folder'],
                       grbroot_dir=aspOutput('GRB'),
                       streamId=nDownlink, 
                       datacatalog_imp="datacatalog",
                       debug=False)

    frequencies = find_intervals()
    for offset, frequency in enumerate(frequencies):
       intervals = frequencies[frequency]
       if frequency == 'six_hours':
          continue
       for interval in intervals:
          args = {'folder' : os.environ['folder'],
                  'interval' : interval.interval,
                  'frequency' : frequency,
                  'nMetStart' : interval.tstart,
                  'nMetStop' : interval.tstop,
                  'GRBOUTPUTDIR' : aspOutput('GRB'),
                  'DRPOUTPUTDIR' : aspOutput('DRP'),
                  'PGWAVEOUTPUTDIR' : aspOutput('PGWAVE'),
                  'PIPELINESERVER' : 'DEV',
                  'ASPLAUNCHERROOT' : _aspLauncherRoot,
                  'datacatalog_imp' : 'datacatalogPROD'}

          for item in args:
             print item, args[item]
          print "\n*******************\n"
    
          stream_id = interval.tstart + offset
          launcher = PipelineCommand('AspLauncher', args, stream=stream_id)
          launcher.run(debug=False)
