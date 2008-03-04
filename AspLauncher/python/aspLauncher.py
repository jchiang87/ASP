"""
@file aspLauncher.py

@brief This script queries the TIMEINTERVALS db table and calculates the
next set of intervals for which the associated ASP tasks are launched.
This is intended to be launched as a subprocess of L1Proc.

Two environment variables need to be provided:

nDownlink = Downlink ID of the current L1Proc instance
folder = Logical folder in the dataCatalog that contains the FT1/2 data

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import databaseAccess as dbAccess

def find_frequencies():
   sql = "select * from FREQUENCIES"
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

#def find_intervals(frequency=None):
#    """Find the most recent interval for each frequency from the
#    FREQUENCIES table and compute the next interval for which the
#    corresponding ASP task must be launched"""
#    if frequency is None:
#        frequencies = find_frequencies()
#    else:
#        frequencies = (frequency, )
#    next_intervals = {}
#    for frequency in frequencies:
#        sql = "SELECT * from TIMEINTERVALS where FREQUENCY='%s'" % frequency
#        def findLastInterval(cursor):
#            lastInterval = -1
#            for entry in cursor:
#                if entry[0] > lastInterval:
#                    lastInterval = entry[0]
#                    tstart = entry[2]
#                    tstop = entry[3]
#            return lastInterval+1, tstop, 2*tstop - tstart
#        next_intervals[frequency] = dbAccess.apply(sql, findLastInterval)
#    return next_intervals

if __name__ == '__main__':
    _asp_path = os.environ['ASP_PATH']
    _version = os.path.split(os.environ['ASPLAUNCHERROOT'])[-1]
    _aspLauncherRoot = os.path.join(_asp_path, 'ASP', 'AspLauncher', _version)

    from PipelineCommand import PipelineCommand

    #
    # Standard output directory for ASP results.  Will this be
    # replaced by a symlink as proposed?
    #
    _output_dir = '/nfs/farm/g/glast/u33/ASP/OpsSim2'

    aspOutput = lambda x : os.path.join(_output_dir, x)

    try:
       os.environ['folder'], os.environ['nDownlink']
    except KeyError:
       os.environ['folder'] = '/Data/OpsSim2/Level1'
#       os.environ['nDownlink'] = '80220001'
#       os.environ['nDownlink'] = '80220002'
       os.environ['nDownlink'] = '80220003'

    print "Using "
    print "DataCatalog folder =", os.environ['folder']
    print "Downlink ID =", os.environ['nDownlink']

    frequencies = find_intervals()
    for frequency in frequencies:
       intervals = frequencies[frequency]
       for interval in intervals:
          args = {'folder' : os.environ['folder'],
                  'nDownlink' : int(os.environ['nDownlink']),
                  'interval' : interval.interval,
                  'frequency' : frequency,
                  'nMetStart' : interval.tstart,
                  'nMetStop' : interval.tstop,
                  'GRBOUTPUTDIR' : aspOutput('GRB'),
                  'DRPOUTPUTDIR' : aspOutput('DRP'),
                  'PGWAVEOUTPUTDIR' : aspOutput('PGWAVE'),
                  'PIPELINESERVER' : 'PROD',
                  'ASPLAUNCHERROOT' : _aspLauncherRoot}

          for item in args:
             print item, args[item]
          print "\n*******************\n"
    
    launcher = PipelineCommand('AspLauncher', args)
    launcher.run()
