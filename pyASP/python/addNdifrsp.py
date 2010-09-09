"""
@brief Function to add NDIFRSP keyword to older FT1 files.
@author J. Chiang
"""
#
# $Header$
#
import pyfits

def addNdifrsp(ft1file):
    ft1 = pyfits.open(ft1file)
    if not ft1['EVENTS'].header.has_key('NDIFRSP'):
        ft1['EVENTS'].header.update('NDIFRSP', 0)
        ft1.writeto(ft1file, clobber=True)
