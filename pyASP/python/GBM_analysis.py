"""
@brief Example script to run through the DC2 GBM Notices and do the
ASP GRB position refinement and LAT spectral analysis.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

from GbmNotice import GbmNotice
from getL1Data import getL1Data
from ft1merge import ft1merge
from refinePosition import refinePosition
from LatGrbSpectrum import LatGrbSpectrum

def notice(id):
    return ('/nfs/farm/g/glast/u33/jchiang/ASP/GRB/Notices/GLG_NOTICE_'
            + id + '.TXT')

duration = 100
ft1Merged = 'FT1_merged.fits'   # temporary file for FT1 data

import glob, sys
files = (notice('080104514'), )
#files = glob.glob('/nfs/farm/g/glast/u33/jchiang/ASP/GRB/Notices/*NOTICE*')
for i, item in enumerate(files):
    gbmNotice = GbmNotice(item)
    if gbmNotice.offAxisAngle() < 60 and not gbmNotice.inSAA():
        print "processing ", i, gbmNotice
        sys.stdout.flush()
        try:
            ft1, ft2 = getL1Data(gbmNotice.start_time - duration,
                                 gbmNotice.start_time + duration)
            ft1merge(ft1, ft1Merged)
            gbmNotice = refinePosition(item, ft1Input=ft1Merged, tsmap=False,
                                       duration=duration)
            like = LatGrbSpectrum(gbmNotice, ft1File=ft1Merged)
        except Exception, message:
            print message
        
