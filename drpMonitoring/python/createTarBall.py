"""
@brief Create a tarball of files that can be used for
reproducing/refining the analysis off-line and copy it to xrootd.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import glob
import shutil
import pipeline
from TarBall import TarBall
from FileStager import FileStager

xrootdGlast = 'root://glast-rdr.slac.stanford.edu//glast'

output_dir = os.environ['OUTPUTDIR']

print "output_dir: ", output_dir

os.chdir(output_dir)

pipeline_server = os.environ['PIPELINESERVER']

process_id = os.environ['PIPELINE_PROCESSINSTANCE']
xrootd_folder = os.environ['xrootd_folder']

xrootd_dir = os.path.join(xrootdGlast, xrootd_folder.strip('/'), 
                          pipeline_server)

print "xrootd_dir: ", xrootd_dir

fileStager = FileStager(process_id, stageArea=output_dir)

archive_name = 'DRP_%s_%s.tar' % tuple(os.getcwd().split('/')[-2:])

outfile = os.path.join(xrootd_dir, archive_name + '.gz')

print "attempting to stage output file to ", outfile

staged_name = fileStager.output(outfile)

print "local staged file name ", staged_name

targets = ('rois.txt', 
           'point_sources.xml',
           'FT2_merged.fits')

region_targets = ('region???_*_model.xml',
                  'region???_events.fits',
                  'expCube.fits',
                  'expMap_sum.fits',
                  'analysis*.py')

regions = glob.glob('region*')
regions.sort()
               
my_tarball = TarBall(archive_name)
for target in targets:
    my_tarball.append(target)
for region in regions:
    for item in region_targets:
        target = os.path.join(region, item)
        my_tarball.append(target)
my_tarball.gzip()

shutil.move(archive_name + '.gz', staged_name)

fileStager.finish()

pipeline.setVariable('tarball_name', outfile)


