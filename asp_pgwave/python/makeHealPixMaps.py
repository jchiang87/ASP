"""
@brief Generate counts and exposure maps using Healpix arrays.
These will be used to compute light curve estimates comprising data
from consecutive downlink analyses.

@author J. Chiang <jchiang@slac.stanford.edu
"""
#
# $Header$
#

import os
from FitsNTuple import FitsNTuple
from generateMaps import CountsArrayFactory, ExposureArrayFactory
import databaseAccess as dbAccess

def get_tlims(ft1file):
    gti = FitsNTuple(ft1file, 'GTI')
    return min(gti.START), max(gti.STOP)

if __name__ == '__main__':
    output_dir = os.environ['OUTPUTDIR']
    os.chdir(output_dir)

    suffix = os.path.basename(output_dir)

    tmin, tmax = get_tlims('FT1_merged.fits')
    
    ft1file = 'Filtered_evt.fits'
    if not os.path.isfile(ft1file):
        raise RuntimeError, "file not found: " + ft1file
    cmapFactory = CountsArrayFactory((ft1file,))
    cmap = cmapFactory.create(tmin, tmax)
    cmapfile = 'counts_%s.fits' % suffix
    cmap.write(cmapfile)

#    #
#    # awful kluge for 55d data: hardwire FT2 file and irfs
#    #
#    ft2file = '/nfs/farm/g/glast/u44/MC-tasks/Interleave55d-GR-v11r17/prune/FT2_55day_patch.fits'
    ft2file = 'FT2_merged.fits'
    
    #
    # Should read this from db table
    #
    sql = ("select IRFS from SOURCEMONITORINGCONFIG where " +
           "STARTDATE<=%i and ENDDATE>=%i" % (tmin, tmin))
    def readIrfs(cursor):
        for entry in cursor:
            return entry[0]
    irfs = dbAccess.apply(sql, readIrfs)

    print "using IRFs: ", irfs

    emapFactory = ExposureArrayFactory(ft2file, irfs=irfs)
    emap = emapFactory.create(tmin, tmax, 'FT1_merged.fits')
    emapfile = 'exposure_%s.fits' % suffix
    emap.write(emapfile)
    
    os.system('chmod 777 *')
