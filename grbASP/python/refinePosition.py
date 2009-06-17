"""
@brief Use gtfindsrc to refine the burst position based on a GCN Notice.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import numpy as num
from FitsNTuple import FitsNTuple
from GcnNotice import GcnNotice
from extractLatData import extractLatData
from GtApp import GtApp
import celgal
import dbAccess
import pipeline
    
gtfindsrc = GtApp('gtfindsrc', 'Likelihood')

def refinePosition(gcn_notice, ft1Input, ft2Input, config,
                   extracted=False, tsmap=True):
    irfs = config.IRFS
    optimizer = config.OPTIMIZER
    try:
        notice = GcnNotice(gcn_notice, skipped=('FERMI_LAT_POSITION',))
    except TypeError:
        notice = gcn_notice

    if notice.offAxisAngle(ft2Input) > 70:
        raise ValueError, ("Burst off-axis angle (from GCN position) "
                           + "> 70 degrees and so lies outside the "
                           + "nominal LAT FOV.")

    if notice.inSAA(ft2Input):
        raise ValueError, ("Burst occurred while LAT was in the SAA.")

    if not extracted:
        ft1_file, lc_file = extractLatData(notice, ft1Input, config)
    else:
        ft1_file = notice.Name + '_LAT_2.fits'
        lc_file = notice.Name + '_LAT_lc_2.fits'

    gtfindsrc['evfile'] = ft1_file
    gtfindsrc['scfile'] = ft2Input
    gtfindsrc['outfile'] = notice.Name + '_findSrc.txt'
    gtfindsrc['irfs'] = irfs
    gtfindsrc['coordsys'] = 'CEL'
    gtfindsrc['ra'] = notice.RA
    gtfindsrc['dec'] = notice.DEC
    gtfindsrc['optimizer'] = optimizer
    gtfindsrc['ftol'] = 1e-10
    gtfindsrc['atol'] = 1e-5
    gtfindsrc['chatter'] = 2

    #
    # kluge if gtfindsrc is run by hand (outside of pipeline)
    # -JC 05-Mar-08
    if not os.path.isfile(gtfindsrc['outfile']):
        gtfindsrc.run()
    results = open(gtfindsrc['outfile']).readlines()
    fields = results[-3].split()
    ra, dec, ts, pos_error = (float(fields[0]), float(fields[1]),
                              float(fields[2]), float(fields[3]))
    if pos_error == 0:
        pos_error = celgal.dist((ra, dec), (notice.RA, notice.DEC))
    if tsmap:
        npix = 20
        mapsize = 6*pos_error
        gttsmap = GtApp('gttsmap', 'Likelihood')
        gttsmap['evfile'] = gtfindsrc['evfile']
        gttsmap['scfile'] = gtfindsrc['scfile']
        gttsmap['irfs'] = gtfindsrc['irfs']
        gttsmap['srcmdl'] = 'none'
        gttsmap['outfile'] = notice.Name + '_tsmap.fits'
        gttsmap['coordsys'] = 'CEL'
        gttsmap['nxpix'] = npix
        gttsmap['nypix'] = npix
        gttsmap['binsz'] = mapsize/float(npix-1)
        gttsmap['xref'] = ra
        gttsmap['yref'] = dec
        print gttsmap.command()
        outfile = os.path.join(os.environ['OUTPUTDIR'], 'gttsmap.par')
        print "writing " + outfile
        gttsmap.pars.write(outfile)

    gtis = FitsNTuple(gtfindsrc['evfile'], 'GTI')
    tmin = gtis.START[0]
    tmax = gtis.STOP[-1]

    notice.ra = ra
    notice.dec = dec
    notice.pos_error = pos_error
    notice.tmin = tmin
    notice.tmax = tmax
    notice.ts = ts
    return notice

def likelyUL(grb_id):
    """For 'zero' duration bursts, we could not extract a LAT light curve, 
    this is a likely upper limit candidate"""
    sql = ("select LAT_FIRST_TIME, LAT_LAST_TIME from GRB " +
           "where GRB_ID=%i and GCAT_FLAG=0" % grb_id)
    def getDuration(cursor):
        for entry in cursor:
            return entry[1] - entry[0]
    duration = dbAccess.apply(sql, getDuration)
    return duration == 0

#
# @todo Need to generalize this somehow.
#
def absFilePath(filename):
    abspath = os.path.abspath(filename)
    return os.path.join('/nfs/farm/g/glast', abspath.split('g.glast.')[1])

if __name__ == '__main__':
    import sys
    from GcnNotice import GcnNotice
    from parfile_parser import Parfile
    from GrbAspConfig import grbAspConfig
    import grb_followup

    output_dir = os.environ['OUTPUTDIR']
    os.chdir(output_dir)

    grb_id = int(os.environ['GRB_ID'])
    gcnNotice = GcnNotice(grb_id, skipped=('FERMI_LAT_POSITION',))
    infiles = open(gcnNotice.Name + '_files')
    ft1File = infiles.readline().strip()
    ft2File = infiles.readline().strip()
    infiles.close()

    config = grbAspConfig.find(gcnNotice.start_time)
    print config

    if likelyUL(grb_id):
        # use parameters from GCN Notice instead of running refinePosition
        gcnNotice.ra = gcnNotice.RA
        gcnNotice.dec = gcnNotice.DEC
        gcnNotice.pos_error = gcnNotice.LOC_ERR
        gcnNotice.tmin = gcnNotice.start_time
        gcnNotice.tmax = gcnNotice.start_time + config.NOMINAL_WINDOW
    else:
        gcnNotice = refinePosition(gcnNotice, ft1File, ft2File, config,
                                   extracted=True, tsmap=True)

    dbAccess.updateGrb(grb_id, LAT_ALERT_TIME=gcnNotice.tmin,
                       LAT_RA=gcnNotice.ra, LAT_DEC=gcnNotice.dec,
                       ERROR_RADIUS=gcnNotice.pos_error,
                       INITIAL_LAT_RA=gcnNotice.RA, 
                       INITIAL_LAT_DEC=gcnNotice.DEC,
                       INITIAL_ERROR_RADIUS=gcnNotice.LOC_ERR,
                       ASP_PROCESSING_LEVEL=1,
                       FT1_FILE="'%s'" % absFilePath(gcnNotice.Name + 
                                                     '_LAT_2.fits'))

    parfile = '%s_pars.txt' % gcnNotice.Name
    pars = Parfile(parfile, fixed_keys=False)
    pars['name'] = gcnNotice.Name
    pars['ra'] = gcnNotice.ra
    pars['dec'] = gcnNotice.dec
    pars['loc_err'] = gcnNotice.pos_error
    pars['tstart'] = gcnNotice.tmin
    pars['tstop'] = gcnNotice.tmax
    pars.write()

    os.system('chmod 777 *')

    #
    # Determine if refined position lies within the nominal FOV
    #
    fov_angle = 90
    offAxisAngle = gcnNotice.offAxisAngle(ft2File, 
                                          (gcnNotice.ra, gcnNotice.dec))
    if offAxisAngle <= fov_angle:
        pipeline.setVariable('within_fov', 'affirmed')
    else:
        print "**************************************************"
        print "Refined burst position off-axis angle: %f.1 deg" % offAxisAngle 
        print "This is outside the nominal FOV angle of %f.1 deg" % fov_angle
        print "Aborting spectral fit."
        print "**************************************************"
