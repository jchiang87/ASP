"""
@brief Use gtfindsrc to refine the burst position based on a GCN Notice

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import numarray as num
from FitsNTuple import FitsNTuple
from GcnNotice import GcnNotice
from extractLatData import extractLatData
from GtApp import GtApp

# defaults for DC2 data
_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'
_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

gtfindsrc = GtApp('gtfindsrc', 'Likelihood')

def refinePosition(gcn_notice, extracted=False, ft1Input=_LatFt1File,
                   ft2Input=_LatFt2File, tsmap=True, duration=100,
                   radius=15, irfs='DSS', optimizer='DRMNFB'):
    try:
        notice = GcnNotice(gcn_notice)
    except TypeError:
        notice = gcn_notice

    if notice.offAxisAngle(ft2Input) > 60:
        raise ValueError, ("Burst off-axis angle (from GCN position) "
                           + "> 60 degrees and so lies outside the "
                           + "nominal LAT FOV.")

    if notice.inSAA():
        raise ValueError, ("Burst occurred while LAT was in the SAA.")

    if not extracted:
        ft1_file, lc_file = extractLatData(notice, ft1File=ft1Input,
                                           duration=duration, radius=radius)
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
    gtfindsrc['chatter'] = 2
    gtfindsrc.run()
    results = open(gtfindsrc['outfile']).readlines()
    fields = results[-3].split()
    ra, dec, ts, pos_error = (float(fields[0]), float(fields[1]),
                              float(fields[2]), float(fields[3]))
    if tsmap:
        npix = 20
        mapsize = 4*pos_error
        gttsmap = GtApp('gttsmap', 'Likelihood')
        gttsmap['evfile'] = gtfindsrc['evfile']
        gttsmap['scfile'] = gtfindsrc['scfile']
        gttsmap['irfs'] = gtfindsrc['irfs']
        gttsmap['srcmdl'] = 'none'
        gttsmap['outfile'] = notice.Name + '_tsmap.fits'
        gttsmap['coordsys'] = 'CEL'
        gttsmap['xref_min'] = ra - mapsize
        gttsmap['xref_max'] = ra + mapsize
        gttsmap['nx'] = npix
        gttsmap['yref_min'] = dec - mapsize
        gttsmap['yref_max'] = dec + mapsize
        gttsmap['ny'] = npix
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

def absFilePath(filename):
    abspath = os.path.abspath(filename)
    return os.path.join('/nfs/farm/g/glast', abspath.split('g.glast.')[1])

if __name__ == '__main__':
    import sys
    from GcnNotice import GcnNotice
    from parfile_parser import Parfile
    import dbAccess
    from createGrbStreams import afterglowStreams
    from GrbAspConfig import grbAspConfig

    output_dir = os.environ['OUTPUTDIR']
    os.chdir(output_dir)

    grb_id = int(os.environ['GRB_ID'])
    gcnNotice = GcnNotice(grb_id)
    infiles = open(gcnNotice.Name + '_files')
    ft1File = infiles.readline().strip()
    ft2File = infiles.readline().strip()
    infiles.close()

    config = grbAspConfig.find(gcnNotice.start_time)
    print config

    gcnNotice = refinePosition(gcnNotice, extracted=True, ft1Input=ft1File,
                               ft2Input=ft2File, tsmap=True, 
                               duration=config.TIMEWINDOW,
                               radius=config.RADIUS,
                               irfs=config.IRFS,
                               optimizer=config.OPTIMIZER)

    dbAccess.updateGrb(grb_id, LAT_ALERT_TIME=gcnNotice.tmin,
                       LAT_RA=gcnNotice.ra, LAT_DEC=gcnNotice.dec,
                       ERROR_RADIUS=gcnNotice.pos_error,
                       INITIAL_RA=gcnNotice.RA, INITIAL_DEC=gcnNotice.DEC,
                       INITIAL_ERROR_RADIUS=gcnNotice.LOC_ERR,
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

    afterglowStreams((os.path.join(output_dir, parfile), ),
                     logicalPath=os.environ['logicalPath'])
