"""
@file aspLauncher.py

@brief Find the time intervals that need to have ASP tasks launched by
querying the ASP database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import databaseAccess as dbAccess

def find_intervals():
    """Find the first interval for each frequency that has not had its
    corresponding task launched"""
    frequencies = ("SixHour", "Daily", "Weekly")
    first_intervals = {}
    for frequency in frequencies:
        sql = "SELECT * from FREQUENCIES where FREQUENCY='%s' and TASK_LAUNCHED='F'" % frequency
        def findFirstInterval(cursor):
            minInterval = -1
            for entry in cursor:
                if entry[0] > minInterval:
                    minInterval = entry[0]
                    tstart = entry[2]
                    tstop = entry[2]
            return minInterval, tstart, tstop
        first_intervals[frequency] = dbAccess.apply(sql, findFirstInterval,
                                                    dbAccess.glastdev)
    return first_intervals

if __name__ == '__main__':
    _asp_path = os.environ['ASP_PATH']
    _version = os.path.split(os.environ['ASPLAUNCHERROOT'])[-1]
    _aspLauncherRoot = os.path.join(_asp_path, 'ASP', 'AspLauncher', _version)

    aspDataDir = lambda x : os.path.join('/nfs/farm/g/glast/u33/ASP/OpsSim2', x)

    intervals = find_intervals()
    args = {'folder' : os.environ['folder'],
            'nDownlink' : int(os.environ['nDownlink'])
            'SixHour_interval' : intervals['SixHour'][0],
            'SixHour_nMetStart' : intervals['SixHour'][1],
            'SixHour_nMetStop' : intervals['SixHour'][2],
            'Daily_interval' : intervals['Daily'][0],
            'Daily_nMetStart' : intervals['Daily'][1],
            'Daily_nMetStop' : intervals['Daily'][2],
            'Weekly_interval' : intervals['Weekly'][0],
            'Weekly_nMetStart' : intervals['Weekly'][1],
            'Weekly_nMetStop' : intervals['Weekly'][2],
            'GRBOUTPUTDIR' : aspDataDir('GRB'),
            'DRPOUTPUTDIR' : aspDataDir('DRP'),
            'PGWAVEOUTPUTDIR' : aspDataDir('PGWAVE'),
            'PIPELINESERVER' : 'PROD',
            'ASPLAUNCHERROOT' : _aspLauncherRoot}
            
    launcher = PipelineCommand('AspLauncher', args)
    launcher.run()
