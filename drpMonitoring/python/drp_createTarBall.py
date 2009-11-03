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
import pipeline
from TarBall import TarBall
from moveToXrootd import moveToXrootd

os.chdir(os.environ['OUTPUTDIR'])

archive_name = 'DRP_%s_%s.tar' % tuple(os.getcwd().split('/')[-2:])

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

outfile = moveToXrootd(archive_name + '.gz', os.environ['OUTPUTDIR'])

pipeline.setVariable('tarball_name', outfile)
