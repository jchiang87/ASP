"""
@file renameOutFiles.py

@brief Rename (copy) the output files from PGWave so that the new
filenames have the interval_number included to allow for easier
browsing from the DataCatalog

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, shutil

def outfile(fn, suffix):
    tokens = fn.split('.')
    return tokens[0] + '_' + suffix + '.' + tokens[1]

def renameOutFiles():
    rootname = 'Filtered_evt'
    exts = ('.fits', '_map.fits', '_map.list', '_map.reg', 
            '_map_pgw_out.fits', '_map_ait.gif', '_map_ait.png')

    infiles = [rootname + ext for ext in exts]

    suffix = os.path.basename(os.environ['OUTPUTDIR'].rstrip('/'))

    for infile in infiles:
        shutil.copy(infile, outfile(infile, suffix))

    shutil.copy('FT2_merged.fits', 'FT2_%s.fits' % suffix)

if __name__ == '__main__':
    os.chdir(os.environ['OUTPUTDIR'])
    renameOutFiles()
