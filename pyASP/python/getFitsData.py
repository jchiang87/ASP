"""
@brief Read the FT1 and FT2 file lists that have been returned by a
query of the datacatalog in a Pipeline II scriptlet.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os, glob, shutil
from FileStager import FileStager

def filter_versions(fitsfiles):
    """Filter the input file list so that only the most recent version 
    of each dataset is returned."""
    try:
        if fitsfiles[0].find('_v') == -1:  # assume no versioning, so just return
            return fitsfiles               # original list
    except IndexError:
        return fitsfiles    # return empty file list
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

def getFileList(filelist, copylist=True):
    if copylist:
        output_dir = os.environ['OUTPUTDIR']
        shutil.copy(filelist, os.path.join(output_dir, filelist))
    fitsfiles = []
    for line in open(filelist):
        if (os.path.isfile(line.strip().strip('+')) or
            line.find('root') == 0):    # file exists or is listed on xrootd
            fitsfiles.append(line.strip().strip('+'))
    fitsfiles.sort()
    return filter_versions(fitsfiles)

def getStagedFileList(filelist, output_dir=None, fileStager=None):
    if fileStager is None:
        if output_dir is None:
            output_dir = os.environ['OUTPUTDIR']
        #
        # Do not clean-up, since staged files would otherwise be deleted
        # when the FileStager object goes out of scope.
        #
        fileStager = FileStager('', stageArea=output_dir, cleanup=False)
    print "getStagedFileList: opening", filelist
    infiles = fileStager.infiles([line.strip() for line in open(filelist)])
    infiles.sort()
    fitsfiles = []
    for item in infiles:
        print "staged file:", item
        if os.path.isfile(item.strip('+')):
            fitsfiles.append(item.strip('+'))
    return filter_versions(fitsfiles)

def match_runs(ft1_files, ft2_files):
    #
    # klugey test to see if we are looking at data from L1Proc
    #
    try:
        if ft1_files[0].find('ph_r') == -1:
            #
            # If not, then just return the input filename lists.
            #
            print "skipping filename matching for FT1/2 files"
            return ft1_files, ft2_files
    except IndexError:
        #
        # We have no FT1 files from the query, so just return empty lists
        #
        return [], []
    #
    # Extract run id from filename (and neglect file version since
    # those need not match)
    #
    runid = lambda x, pref : x.split(pref)[-1].split('v')[0]

    ft1_runs = set([runid(x, 'ph_') for x in ft1_files])
    ft2_runs = set([runid(x, 'pt_') for x in ft2_files])
    matched = ft1_runs.intersection(ft2_runs)

    ft1 = [x for x in ft1_files if runid(x, 'ph_') in matched]
    ft1.sort()
    ft2 = [x for x in ft2_files if runid(x, 'pt_') in matched]
    ft2.sort()

    return ft1, ft2

def getFitsData(ft1list='Ft1FileList', ft2list='Ft2FileList', copylist=True):
    ft1, ft2 = getFileList(ft1list, copylist), getFileList(ft2list, copylist)
    return match_runs(ft1, ft2)

def getStagedFitsData(ft1list='Ft1FileList', ft2list='Ft2FileList',
                      fileStager=None):
    ft1, ft2 = (getStagedFileList(ft1list, fileStager=fileStager),
                getStagedFileList(ft2list, fileStager=fileStager))
    return match_runs(ft1, ft2)
