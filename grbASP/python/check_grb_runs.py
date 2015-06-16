"""
@brief The function ok_to_launch queries the RUN table to determine the
L1PROCSTATUS for the runs that may contain a given GRB trigger time.
If the candidate runs have all finalized, True is returned.  If they have
not all finalized, or if a run subsequent to the GRB trigger time is not
found, then False is returned.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
import numpy
import databaseAccess as dbAccess

pII = ('/@pipeline-II',)

def get_runs(cursor):
    run_status = []
    for entry in cursor:
        run_status.append((entry[0], entry[1]))
    return run_status

def ok_to_launch(trigger_time, half_window=100):
    """Determine from RUN db table the status of runs that may
    be associated with this burst trigger time.  If no candidate runs
    are found, return False (assuming later runs may still arrive).
    If the candidate runs have been finalized, then return True.
    If any of the candidate runs have not been finalized, return False.

    This can only be run in PROD, since the RUN table is not relevant in
    DEV, so use PIPELINESERVER env var to distinguish.
    """
    if os.environ['PIPELINESERVER'] != 'PROD':
        return True

    #
    # Interval to be considered.
    #
    tmin = trigger_time - half_window
    tmax = trigger_time + half_window

    #
    # Find all runs after tmax to see if the data have arrived.
    #
    sql = "select runid from run where runid>%i" % tmax
    have_runs = dbAccess.apply(sql, lambda curs : [x[0] for x in curs],
                               connection=pII)
    
    #print "have_runs", have_runs

    if not have_runs:
        return False, ()

    #
    # Find runs that may cover this interval; cast a wide (day-long) net:
    #
    sql = ("select runid, l1procstatus from run where runid>%i and runid<%i "
           % (tmin-43200, tmax + 43200) + "order by runid asc")
    runs = dbAccess.apply(sql, get_runs, connection=pII)

    runids = numpy.array([x[0] for x in runs])

    imin = max(numpy.where(runids < tmin)[0])
    imax = max(numpy.where(runids < tmax)[0])

    for i in range(imin, imax+1):
        if runs[i][1] not in ("Complete", "Incomplete"):
            return False, runs[imin:imax+1]

    return True, runs[imin:imax+1]

if __name__ == '__main__':
    times = (236600017, 236692340, 236804413, 236985253, 237112073, 237149308)
    for time in times:
        print time, ok_to_launch(time)
