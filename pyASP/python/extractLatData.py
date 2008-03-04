"""
@brief Extract LAT data based on a GBM notice
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num
from FitsNTuple import FitsNTuple
from BayesBlocks import BayesBlocks
from GtApp import GtApp

gtselect = GtApp('gtselect')
gtbin = GtApp('gtbin')

_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'

def extractLatData(gbmNotice, ft1File=_LatFt1File, duration=100, radius=15):
    gtselect['infile'] = ft1File
    gtselect['outfile'] = gbmNotice.Name + '_LAT.fits'
    gtselect['ra'] = gbmNotice.RA
    gtselect['dec'] = gbmNotice.DEC
    gtselect['rad'] = radius
    gtselect['tmin'] = gbmNotice.start_time - duration
    gtselect['tmax'] = gbmNotice.start_time + duration
    gtselect.run()

    gtbin['evfile'] = gtselect['outfile']
    gtbin['outfile'] = gbmNotice.Name + '_LAT_lc.fits'
    gtbin['algorithm'] = 'LC'
    gtbin['timebinalg'] = 'LIN'
    gtbin['tstart'] = gbmNotice.start_time - duration
    gtbin['tstop'] = gbmNotice.start_time + duration
    gtbin['deltatime'] = 0.1
    gtbin.run()
    
    events = FitsNTuple(gtselect['outfile'], 'EVENTS')
    bb = BayesBlocks(events.TIME, 4)
    lc = bb.lightCurve()
    x, y = lc.dataPoints()

    try:
#        tmin, tmax = burst_interval(gtbin['outfile'])
        tmin, tmax = x[1], x[-2]
        gtselect['infile'] = gtselect['outfile']
        gtselect['outfile'] = gbmNotice.Name + '_LAT_2.fits'
        gtselect['tmin'] = tmin
        gtselect['tmax'] = tmax
        gtselect.run()
        gtbin['evfile'] = gtselect['outfile']
        gtbin['outfile'] = gbmNotice.Name + '_LAT_lc_2.fits'
        gtbin['tstart'] = tmin
        gtbin['tstop'] = tmax
        gtbin.run()
    except:
        pass

    return gtselect['outfile'], gtbin['outfile']

def burst_interval(lc_file, minrate=30):
    lc = FitsNTuple(lc_file, 'RATE')
    rate = lc.COUNTS/lc.TIMEDEL
    indx = num.where(rate > minrate)
    times = lc.TIME[indx]
    dts = lc.TIMEDEL[indx]
    return times[0] - dts[0], times[-1] + dts[-1]

if __name__ == '__main__':
    import numarray as num
    from GbmNotice import GbmNotice
    import hippoplotter as plot
    notice = GbmNotice('GLG_NOTICE_080101283.TXT')
    lc_file = extractLatData(notice)
#    lc_file = notice.Name + '_LAT_lc.fits'
    nt, tup = plot.FitsNTuple(lc_file, 'RATE')
    nt.addColumn('rate', tup.COUNTS/tup.TIMEDEL)
    nt.addColumn('rate_err', num.sqrt(tup.COUNTS)/tup.TIMEDEL)
    plot.XYPlot(nt, 'TIME', 'rate', yerr='rate_err')
