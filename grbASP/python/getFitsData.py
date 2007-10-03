"""
@brief Read the FT1 and FT2 file lists that have been returned by a
query of the datacatalog in a Pipeline II scriptlet.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, shutil

def getFileList(filelist):
    output_dir = os.environ['OUTPUTDIR']
    shutil.copy(filelist, os.path.join(output_dir, filelist))
    fitsfiles = []
    for line in open(filelist):
        fitsfiles.append(line.strip())
    return fitsfiles

def getFitsData(ft1list='Ft1FileList', ft2list='Ft2FileList'):
    return getFileList(ft1list), getFileList(ft2list)
