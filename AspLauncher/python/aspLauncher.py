"""
@file aspLauncher.py

@brief This script queries the TIMEINTERVALS db table and calculates the
next set of intervals for which the associated ASP tasks are launched.
This is intended to be launched as a subprocess of L1Proc.
Only two environment variables need to be provided:

nDownlink = Downlink ID of the current L1Proc instance
folder = Logical folder in the dataCatalog that should be queried for
         the FT1/2 data

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
   return dbAccess.apply(sql, getFrequencies, dbAccess.glastdev)

def find_intervals():
    """Find the most recent interval for each frequency from the
    FREQUENCIES table and compute the next interval for which the
    corresponding ASP task must be launched"""
    frequencies = find_frequencies()
    next_intervals = {}
    for frequency in frequencies:
        sql = "SELECT * from TIMEINTERVALS where FREQUENCY='%s'" % frequency
        def findLastInterval(cursor):
            lastInterval = -1
            for entry in cursor:
                print len(entry)
                print entry
                if entry[0] > lastInterval:
                    lastInterval = entry[0]
                    tstart = entry[2]
                    tstop = entry[3]
            return lastInterval+1, tstop, 2*tstop - tstart
        next_intervals[frequency] = dbAccess.apply(sql, findLastInterval,
                                                   dbAccess.glastdev)
    return next_intervals

if __name__ == '__main__':
    _asp_path = os.environ['ASP_PATH']
    _version = os.path.split(os.environ['ASPLAUNCHERROOT'])[-1]
    _aspLauncherRoot = os.path.join(_asp_path, 'ASP', 'AspLauncher', _version)

    aspOutput = lambda x : os.path.join('/nfs/farm/g/glast/u33/ASP/OpsSim2', x)

    os.environ['folder'] = '/Data/OpsSim2/Level1'
    os.environ['nDownlink'] = 80219002

    intervals = find_intervals()
    args = {'folder' : os.environ['folder'],
            'nDownlink' : int(os.environ['nDownlink']),
            'SixHour_interval' : intervals['six_hour'][0],
            'SixHour_nMetStart' : intervals['six_hour'][1],
            'SixHour_nMetStop' : intervals['six_hour'][2],
            'Daily_interval' : intervals['daily'][0],
            'Daily_nMetStart' : intervals['daily'][1],
            'Daily_nMetStop' : intervals['daily'][2],
            'Weekly_interval' : intervals['weekly'][0],
            'Weekly_nMetStart' : intervals['weekly'][1],
            'Weekly_nMetStop' : intervals['weekly'][2],
            'GRBOUTPUTDIR' : aspOutput('GRB'),
            'DRPOUTPUTDIR' : aspOutput('DRP'),
            'PGWAVEOUTPUTDIR' : aspOutput('PGWAVE'),
            'PIPELINESERVER' : 'PROD',
            'ASPLAUNCHERROOT' : _aspLauncherRoot}

    for item in args:
        print item, args[item]
    
#    launcher = PipelineCommand('AspLauncher', args)
#    launcher.run()
