"""
@brief Function to determine event analysis pass version from PASS_VER
header keyword of FT1 EVENTS extension.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numpy as np
import pyfits

def pass_version(ft1file):
    ft1 = pyfits.open(ft1file)
    try:
        return ft1['EVENTS'].header['PASS_VER']
    except KeyError:
        return 'NONE'

class EventClassSelection(object):
    """
    Based on the PASS_VER keyword in the input FT1 file, this class
    provides the standard evclass values corresponding to TRANSIENT
    and SOURCE class selections.
    """
    def __init__(self, ft1file):
        super(EventClassSelection, self).__init__()
        self.pass_version = pass_version(ft1file)
        self._transient = None
        self._source = None
    @property
    def transient(self):
        if self._transient is None:
            if self.pass_version.startswith('P7'):
                self._transient = 0
            elif self.pass_version.startswith('P8'):
                self._transient = 16   # TRANSIENT020
            else:
                self._transient = 'INDEF'
        return self._transient
    @property
    def source(self):
        if self._source is None:
            if self.pass_version.startswith('P7'):
                self._source = 2
            elif self.pass_version.startswith('P8'):
                self._source = 128
            else:
                self._source = 'INDEF'
        return self._source

def createTestFile(pass_ver, outfile='test_ft1.fits'):
    output = pyfits.HDUList()
    output.append(pyfits.PrimaryHDU())
    ra = pyfits.Column(name='RA', format='1E', array=np.zeros(10))
    dec = pyfits.Column(name='DEC', format='1E', array=np.zeros(10))
    events = pyfits.new_table([ra, dec])
    events.name = 'EVENTS'
    events.header['PASS_VER'] = pass_ver
    output.append(events)
    output.writeto(outfile, clobber=True)

if __name__ == '__main__':
    import os
    test_values = {'NONE' : ('INDEF', 'INDEF'),
                   'P7REP' : (0, 2),
                   'P8R2' : (16, 128)}
    evfile = 'test_ft1.fits'
    for pass_ver in ('NONE', 'P7REP', 'P8R2'):
        createTestFile(pass_ver, outfile=evfile)
        evclass = EventClassSelection(evfile)
        assert(evclass.transient == test_values[pass_ver][0])
        assert(evclass.source == test_values[pass_ver][1])
        os.remove(evfile)
