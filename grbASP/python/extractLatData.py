"""
@brief Extract LAT data based on a GCN notice
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num
from FitsNTuple import FitsNTuple
from BayesBlocks import BayesBlocks
from GtApp import GtApp

gtselect = GtApp('gtselect', 'dataSubselector')
gtbin = GtApp('gtbin', 'evtbin')

_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'

def extractLatData(gcnNotice, ft1File=_LatFt1File, duration=100, radius=15):
    gtselect['infile'] = ft1File
    gtselect['outfile'] = gcnNotice.Name + '_LAT.fits'
    gtselect['ra'] = gcnNotice.RA
    gtselect['dec'] = gcnNotice.DEC
    gtselect['rad'] = radius
    gtselect['tmin'] = gcnNotice.start_time - duration
    gtselect['tmax'] = gcnNotice.start_time + duration
    gtselect.run()

    gtbin['evfile'] = gtselect['outfile']
    gtbin['outfile'] = gcnNotice.Name + '_LAT_lc.fits'
    gtbin['algorithm'] = 'LC'
    gtbin['tbinalg'] = 'LIN'
    gtbin['tstart'] = gcnNotice.start_time - duration
    gtbin['tstop'] = gcnNotice.start_time + duration
    gtbin['dtime'] = 0.1
    gtbin.run()
    
    events = FitsNTuple(gtselect['outfile'], 'EVENTS')
    bb = BayesBlocks(events.TIME, 4)
    lc = bb.lightCurve()
    x, y = lc.dataPoints()

    try:
        if len(x) == 2:
            tmin, tmax = tuple(x)
        else:
            tmin, tmax = x[1], x[-2]
        gtselect['infile'] = gtselect['outfile']
        gtselect['outfile'] = gcnNotice.Name + '_LAT_2.fits'
        gtselect['tmin'] = tmin
        gtselect['tmax'] = tmax
        gtselect.run()
        gtbin['evfile'] = gtselect['outfile']
        gtbin['outfile'] = gcnNotice.Name + '_LAT_lc_2.fits'
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
    import os, shutil
    from GcnNotice import GcnNotice
    from getFitsData import getFitsData
    from ft1merge import ft1merge

    ft1, ft2 = getFitsData()
    os.chdir(os.environ['OUTPUTDIR'])
    gcnNotice = GcnNotice(int(os.environ['GRB_ID']))

    ft1Merged = 'FT1_merged.fits'
    ft1merge(ft1, ft1Merged)

    fmerge = GtApp('fmerge')
    fmerge['infiles'] = '@Ft2FileList'
    fmerge['outfile'] = 'FT2_merged.fits'
    fmerge['clobber'] = 'yes'
    fmerge['columns'] = '" "'
    fmerge['mextname'] = '" "'
    fmerge['lastkey'] = '" "'
    fmerge.run()

    duration = 100   # this should be read from the GRB_ASP_CONFIG db table
    ft1_extracted, lcFile = extractLatData(gcnNotice, ft1Merged, 
                                           duration=duration, radius=15)
    outfile = open('%s_files' % gcnNotice.Name, 'w')
    outfile.write('%s\n%s\n' % (ft1_extracted, fmerge['outfile']))
    outfile.close()

    os.system('chmod 777 *')
