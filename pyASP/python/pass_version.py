"""
@brief Function to determine event analysis pass version from PASS_VER
header keyword of FT1 EVENTS extension.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import pyfits

def pass_version(ft1file):
    ft1 = pyfits.open(ft1file)
    try:
        return ft1['EVENTS'].header['PASS_VER']
    except KeyError:
        return 'NONE'

if __name__ == '__main__':
    print pass_version('/nfs/farm/g/glast/u54/jchiang/GRB/Swift_ULs/240364157/FT1.fits')
    print pass_version('/nfs/farm/g/glast/u54/jchiang/GRB/Swift_ULs/Pass7/240239424/FT1.fits')
