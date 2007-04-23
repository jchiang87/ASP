"""
@brief Use gtfindsrc to refine the burst position based on a GBM Notice

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import numarray as num
from FitsNTuple import FitsNTuple
from GbmNotice import GbmNotice
from extractLatData import extractLatData
from GtApp import GtApp

# defaults for DC2 data
_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'
_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

gtfindsrc = GtApp('gtfindsrc', 'Likelihood')

def refinePosition(gbm_notice, extracted=False, ft1Input=_LatFt1File,
                   ft2Input=_LatFt2File, tsmap=True, duration=100,
                   radius=15):
    try:
        notice = GbmNotice(gbm_notice)
    except TypeError:
        notice = gbm_notice

    if notice.offAxisAngle() > 60:
        raise ValueError, ("Burst off-axis angle (from GBM position) "
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
    gtfindsrc['rspfunc'] = 'DSS'
    gtfindsrc['use_lb'] = 'no'
    gtfindsrc['lon0'] = notice.RA
    gtfindsrc['lat0'] = notice.DEC
    gtfindsrc['optimizer'] = 'DRMNGB'
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
        gttsmap['rspfunc'] = gtfindsrc['rspfunc']
        gttsmap['source_model_file'] = 'none'
        gttsmap['outfile'] = notice.Name + '_tsmap.fits'
        gttsmap['use_lb'] = 'no'
        gttsmap['ra_min'] = ra - mapsize
        gttsmap['ra_max'] = ra + mapsize
        gttsmap['nra'] = npix
        gttsmap['dec_min'] = dec - mapsize
        gttsmap['dec_max'] = dec + mapsize
        gttsmap['ndec'] = npix
        print gttsmap.command()
        outfile = os.path.join(os.environ['OUTPUTDIR'], 'gttsmap.par')
        print "writing " + outfile
        gttsmap.pars.write(outfile)
        #gttsmap.run()

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

if __name__ == '__main__':
    import os, sys
    from GbmNotice import GbmNotice
    from parfile_parser import Parfile
    from createGrbStreams import afterglowStreams
    
    output_dir = os.environ['OUTPUTDIR']
    os.chdir(output_dir)
    gbmNotice = GbmNotice(os.environ['GBMNOTICE'])
    infiles = open(gbmNotice.Name + '_files')
    ft1File = infiles.readline().strip()
    ft2File = infiles.readline().strip()
    infiles.close()
    gbmNotice = refinePosition(gbmNotice, extracted=True, ft1Input=ft1File,
                               ft2Input=ft2File, tsmap=True, duration=100,
                               radius=15)
    parfile = '%s_pars.txt' % gbmNotice.Name
    pars = Parfile(parfile, fixed_keys=False)
    pars['name'] = gbmNotice.Name
    pars['ra'] = gbmNotice.ra
    pars['dec'] = gbmNotice.dec
    pars['loc_err'] = gbmNotice.pos_error
    pars['tstart'] = gbmNotice.tmin
    pars['tstop'] = gbmNotice.tmax
    pars.write()

    os.system('chmod 777 *')

#    afterglowStreams((os.path.join(output_dir, parfile), ))
