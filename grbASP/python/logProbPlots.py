"""
@brief Create plots of log-probabilities for blind search.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
#
# Need to set this first so that pylab can write .matplotlib
#
os.environ['MPLCONFIGDIR'] = os.environ['GRBROOTDIR']

import sys
import datetime
import numpy as num
import pylab
from FitsNTuple import FitsNTuple

def utc_day(met):
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    missionStart = datetime.datetime(2001, 1, 1, 0, 0, 0)
    dt = datetime.timedelta(0, met)
    utc = missionStart + dt
    my_date = ("%3s %02i %3s %02i UT" %
               (weekdays[utc.weekday()], utc.day, months[utc.month-1],
                utc.year % 2000))
    return my_date

def time_history(time, logProbs, threshold, tstart, tstop, outfile=None):
    axisRange = (min(time), max(time), min(logProbs)-10, max(logProbs))
    pylab.plot(time, logProbs, 'k')
    pylab.xlabel('Time (MET)')
    pylab.ylabel('log-probability')
    startdate = utc_day(tstart)
    enddate = utc_day(tstop)
    title = 'ASP Blind Search results\n%s' % startdate
    if startdate != enddate:
        title += ' - %s' % enddate
    pylab.title(title)
    pylab.plot([min(time), max(time)], [threshold, threshold], 'k:')
    pylab.axis(axisRange)
    if outfile is None:
        pylab.show()
    else:
        pylab.savefig(outfile)
        pylab.close()

def xyhist(xvals, yvals, tstart, tstop, nx=50, ny=50, outfile=None):
    xmin, xmax = min(xvals)-1, max(xvals)+1
    ymin, ymax = min(yvals)-1, max(yvals)+1
    dx = (xmax - xmin)/(nx-1)
    dy = (ymax - ymin)/(ny-1)

    valopt = xvals[0] + yvals[0]
    xopt, yopt = xvals[0], yvals[0]
    data = num.zeros((nx, ny))
    for xx, yy in zip(xvals, yvals):
        ix = int((xx - xmin)/dx)
        iy = int((yy - ymin)/dy)
        try:
            data[iy][ix] += 1
        except IndexError:
            print ix, iy
        if xx + yy < valopt:
            valopt = xx + yy
            xopt, yopt = xx, yy

    data = data.tolist()
    data.reverse()
    data = num.array(data)

    axisRange = (xmin, xmax, ymin, ymax)
    pylab.imshow(data, interpolation='nearest',
                 cmap=pylab.cm.spectral_r, extent=axisRange, 
                 aspect=dx/dy)
    pylab.colorbar(ticks=range(int(min(data.flat)), int(max(data.flat))+2))

    pylab.plot([xopt], [yopt], 'x', markersize=10, color='k')
    pylab.axis(axisRange)

    pylab.xlabel('temporal log-probability')
    pylab.ylabel('spatial log-probability')
    startdate = utc_day(tstart)
    enddate = utc_day(tstop)
    title = 'ASP Blind Search results\n%s' % startdate
    if startdate != enddate:
        title += ' - %s' % enddate
    pylab.title(title)
    
    if outfile is None:
        pylab.show()
    else:
        pylab.savefig(outfile)
        pylab.close()

def createPlots(logProbFile, downlinkId, threshold):
    foo = FitsNTuple(logProbFile)

    logProbDistFile = 'logProbs_%s.png' % downlinkId
    timeHistoryFile = 'time_history_%s.png' % downlinkId

    xyhist(foo.logL_temporal, foo.logL_spatial, foo.time[0], foo.time[-1],
           outfile=logProbDistFile)
    time_history(foo.time, foo.logL_temporal + foo.logL_spatial, threshold,
                 foo.time[0], foo.time[-1], 
                 outfile=timeHistoryFile)
    return logProbDistFile, timeHistoryFile

if __name__ == '__main__':
    from MultiPartMailer import MultiPartMailer

    message = \
"""
ASP GRB_blind_search found a burst candidate at

 (RA, Dec) = (23.776, 69.013)

with trigger time

 Sat 26 Jul 08 02:17:07 UT
 MET = 238731427.455
"""
    mailer = MultiPartMailer('ASP blind search candidate')
    mailer.add_text(message)
    mailer.add_image('logProbs.png')
    mailer.add_image('time_history.png')
    mailer.finish()
    mailer.send('jchiang@slac.stanford.edu', 
                'jchiang87@gmail.com')
