"""
@brief Code to access and manipulate timeintervals and frequencies
tables for the flare detection and source monitoring applications.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import databaseAccess as dbAccess

def getFrequencies(freqtype=0):
   sql = "select FREQUENCY, DURATION from FREQUENCIES where TYPE=%i" % freqtype
   def getFreqs(cursor):
       freqs = {}
       for entry in cursor:
           freqs[entry[0]] = entry[1]
       return freqs
   return dbAccess.apply(sql, getFreqs)

class TimeInterval(object):
   def __init__(self, entry):
      self.interval = entry[0]
      self.frequency = entry[1]
      self.tstart = entry[2]
      self.tstop = entry[3]
      self.is_processed = entry[4]

def unhandledIntervals(freqtype=0):
   """Find unhandled intervals"""
   sql = ("SELECT interval_number, frequency, tstart, tstop, is_processed " +
          "from TIMEINTERVALS where IS_PROCESSED=0 " +
          "order by interval_number asc")
   frequencies = getFrequencies(freqtype=freqtype)
   unhandled = {}
   for freq in frequencies:
      unhandled[freq] = []
   def findUnhandled(cursor, unhandled=unhandled):
      for entry in cursor:
         timeInterval = TimeInterval(entry)
         try:
             unhandled[timeInterval.frequency].append(timeInterval)
         except KeyError:
             pass
      return unhandled
   try:
      return dbAccess.apply(sql, findUnhandled)
   except dbAccess.cx_Oracle.DatabaseError, message:
      print message
      print sql

def insertInterval(id, freq, tstart, tstop):
    sql_template = ("insert into TIMEINTERVALS (INTERVAL_NUMBER, FREQUENCY, "
                    + "TSTART, TSTOP) values (%i, '%s', %i, %i)")
    sql = sql_template % (id, freq, tstart, tstop)
    dbAccess.apply(sql)

def insertNewIntervals(nMetStart, nMetStop, freqtype=0):
    freqs = getFrequencies(freqtype)
    for freq in freqs:
        sql = ("select interval_number, tstart, tstop from timeintervals " +
               "where frequency='%s' " % freq +
               "and (tstart <= %i or tstop >= %i) " % (nMetStart, nMetStop) +
               "order by interval_number")
        intervals = dbAccess.apply(sql, lambda curs : [tuple(x) for x in curs])
        interval_number = intervals[-1][0]
        tstop = intervals[-1][-1]
        while tstop < nMetStop:
            interval_number += 1
            tstart = tstop
            tstop += freqs[freq]
            insertInterval(interval_number, freq, tstart, tstop)
            print "Inserting into TIMEINTERVALS table:", \
                freq, interval_number, tstart, tstop
        print
