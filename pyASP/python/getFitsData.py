"""
@brief Read the FT1 and FT2 file lists that have been returned by a
query of the datacatalog in a Pipeline II scriptlet.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, glob, shutil

def filter_versions(fitsfiles):
    """Filter the input file list so that only the most recent version 
    of each dataset is returned."""
    prefixes = {}
    for item in fitsfiles:
        tokens = item.split('_v')
        dirname = os.path.dirname(tokens[0])
        basename = os.path.basename(tokens[0])
        prefixes[basename] = dirname, tokens[1]
    outfiles = []
    basenames = prefixes.keys()
    # sort by basename (with version info sliced off) to get time ordering
    basenames.sort()
    for item in basenames:
        fullpath = os.path.join(prefixes[item][0], 
                                '_'.join((item, 'v'+prefixes[item][1])))
        outfiles.append(fullpath)
    return outfiles

def getFileList(filelist):
    output_dir = os.environ['OUTPUTDIR']
    shutil.copy(filelist, os.path.join(output_dir, filelist))
    fitsfiles = []
    for line in open(filelist):
        if os.path.isfile(line.strip().strip('+')):    # file exists
            fitsfiles.append(line.strip().strip('+'))
    return filter_versions(fitsfiles)

def getFitsData(ft1list='Ft1FileList', ft2list='Ft2FileList'):
    return getFileList(ft1list), getFileList(ft2list)
