"""
@brief Create a tarball of useful files used in the GRB_afterglow task for 
storage on xrootd.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import pipeline
from TarBall import TarBall
from moveToXrootd import moveToXrootd

output_dir = os.environ['GRBROOTDIR']
os.chdir(output_dir)

archive_name = "GRB_afterglow_%s.tar" % os.getcwd().split('/')[-1]

targets = ('GRB*_L1.fits',
           'FT2_merged.fits',
           'exp*_GRB*.fits',
           'GRB*_afterglow_*',
           'GRB*_model.xml')

my_tarball = TarBall(archive_name)
for target in targets:
    my_tarball.append(target)
my_tarball.gzip()

outfile = moveToXrootd(archive_name + '.gz', output_dir)
pipeline.setVariable('tarball_name', outfile)
