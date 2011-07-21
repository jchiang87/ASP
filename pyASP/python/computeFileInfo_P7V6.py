"""
@brief Compute the file information for downlink files and write them
to a text file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import pipeline

print pipeline.__file__

ft1_fileList = "/nfs/farm/g/glast/u54/asp/AspSims/P7V6_P120/ft1_filelist"
ft2_fileList = "/nfs/farm/g/glast/u54/asp/AspSims/P7V6_P120/ft2_filelist"
ext_fileList = "/nfs/farm/g/glast/u54/asp/AspSims/P7V6_P120/ext_filelist"

numfiles = len([x for x in open(ft1_fileList, 'r') if x.find("#") != 0])

pipeline.setVariable('ft1_fileList', ft1_fileList)
pipeline.setVariable('ft2_fileList', ft2_fileList)
pipeline.setVariable('ext_fileList', ext_fileList)
pipeline.setVariable('numfiles', numfiles)
