"""
@brief Use the fmerge FTOOL to merge FT1 files, combining both the
EVENTS and GTI extensions.  It is implicitly assumed that the time
intervals covered by the files do not overlap and that any other
selections, such as acceptance cone, energy range, or event class
cuts, are the same for all of the files.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import pyfits
from GtApp import GtApp

fmerge = GtApp('fmerge')
fchecksum = GtApp('fchecksum')

def _fileList(infiles, extnum=1):
    filelist = 'ft1merge_file_list'
    if len(infiles) > 1000:
        raise RuntimeError, ('Number of input files exceeds 1000, '
                             + 'the fmerge maximum.')
    infile_list = open(filelist, 'w')
    for item in infiles:
        infile_list.write(item + ('[%s]\n' % extnum))
    infile_list.close()
    return filelist

def _getTimeKeywords(infiles, extnum=1):
    header = pyfits.open(infiles[0])[extnum].header
    tstart = header['TSTART']
    tstop = header['TSTOP']
    for item in infiles[1:]:
        header = pyfits.open(item)[extnum].header
        if header['TSTART'] < tstart:
            tstart = header['TSTART']
        if header['TSTOP'] > tstop:
            tstop = header['TSTOP']
    return tstart, tstop

def ft1merge(infiles, outfile):
    tstart, tstop = _getTimeKeywords(infiles)
    fmerge['infiles'] = '"@' + _fileList(infiles) + '"'
    fmerge['outfile'] = outfile
    fmerge['clobber'] = 'yes'
    fmerge['columns'] = '" "'
    fmerge['mextname'] = '" "'
    fmerge['lastkey'] = '" "'
    fmerge.run()

    fmerge['infiles'] = '"@' + _fileList(infiles, 'GTI') + '"'
    fmerge['outfile'] = 'ft1merge_gti.fits'
    fmerge.run()

    foo = pyfits.open(outfile)
    gti = pyfits.open(fmerge['outfile'])
    foo.append(gti['GTI'])

    foo[0].header['TSTART'] = tstart
    foo[0].header['TSTOP'] = tstop
    foo[1].header['TSTART'] = tstart
    foo[1].header['TSTOP'] = tstop
    foo[0].header['FILENAME'] = outfile
    foo.writeto(outfile, clobber=True)

    fchecksum['infile'] = outfile
    fchecksum['update'] = 'yes'
    fchecksum['datasum'] = 'yes'
    fchecksum.run()
    
    try:
        os.remove(fmerge['outfile'])
    except OSError:
        pass
    try:
        filename = fmerge['infiles'].strip('"').strip('@')
        os.remove(filename)
    except OSError:
        pass

if __name__ == '__main__':
    L1DataPath = '/nfs/farm/g/glast/u33/jchiang/DC2/Downlinks'
    infiles = [os.path.join(L1DataPath, 'downlink_%04i.fits' % i)
             for i in range(4)]
    ft1merge(infiles, 'foo.fits')
