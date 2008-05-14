"""
@brief Extract LAT data based on a GCN notice
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numpy as num
from FitsNTuple import FitsNTuple
from BayesBlocks import BayesBlocks
from GtApp import GtApp
import dbAccess

gtselect = GtApp('gtselect', 'dataSubselector')
gtbin = GtApp('gtbin', 'evtbin')

def extractLatData(gcnNotice, ft1File, config):
    duration = config.TIMEWINDOW
    radius = config.RADIUS
    gtselect['infile'] = ft1File
    gtselect['outfile'] = gcnNotice.Name + '_LAT.fits'
    gtselect['ra'] = gcnNotice.RA
    gtselect['dec'] = gcnNotice.DEC
    gtselect['rad'] = radius
    gtselect['tmin'] = gcnNotice.start_time - duration
    gtselect['tmax'] = gcnNotice.start_time + duration
    gtselect['zmax'] = 100 # need to retrieve this from db table
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
        grb_id = int(os.environ['GRB_ID'])
        if len(x) == 2:
            # No change points found.  Flag this burst for upper limit
            # calculation by setting LAT_FIRST_TIME=LAT_LAST_TIME = 0
            # and use nominal time window starting at trigger time.
            tmin = gcnNotice.start_time
            dbAccess.updateGrb(grb_id, LAT_FIRST_TIME=tmin, 
                               LAT_LAST_TIME=tmin)
            try:
                tmax = tmin + config.NOMINAL_WINDOW
            except AttributeError:
                tmax = tmin + 60
        else:
            tmin, tmax = x[1], x[-2]
            dbAccess.updateGrb(grb_id, LAT_FIRST_TIME=tmin, LAT_LAST_TIME=tmax)
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
    from FileStager import FileStager
    from getFitsData import getStagedFitsData
    from ft1merge import ft1merge, ft2merge
    from GrbAspConfig import grbAspConfig

    output_dir = os.environ['OUTPUTDIR']
    
    fileStager = FileStager('stagingDir', stageArea=output_dir, 
                            messageLevel="INFO")
    ft1, ft2 = getStagedFitsData(fileStager=fileStager)

    os.chdir(output_dir)
    gcnNotice = GcnNotice(int(os.environ['GRB_ID']))

    ft1Merged = 'FT1_merged.fits'
    print "merging FT1 files:"
    for item in ft1:
        print item
    ft1merge(ft1, ft1Merged)
    
    ft2Merged = 'FT2_merged.fits'
    print "merging FT2 files:"
    for item in ft2:
        print item
    ft2merge(ft2, ft2Merged)

    config = grbAspConfig.find(gcnNotice.start_time)
    ft1_extracted, lcFile = extractLatData(gcnNotice, ft1Merged, config)
    outfile = open('%s_files' % gcnNotice.Name, 'w')
    outfile.write('%s\n%s\n' % (ft1_extracted, ft2Merged))
    outfile.close()

    fileStager.finish()

    os.system('chmod 777 *')
