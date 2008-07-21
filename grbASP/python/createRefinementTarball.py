"""
@brief Create a tarball of useful files used in the GRB_refinement task for 
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

output_dir = os.environ['OUTPUTDIR']
os.chdir(output_dir)

archive_name = "GRB_refinement_%s.tar" % os.getcwd().split('/')[-1]

targets = ('GRB*_BB_lc.dat',
           'GRB*_LAT.fits',
           'FT2_merged.fits',
           'GRB*_Notice.txt',
           'GRB*_tsmap.fits',
           'GRB*_exp*.fits',
           'GRB*_grb_spec.fits',
           'GRB*_model.xml',
           'GRB*_pars.txt')

my_tarball = TarBall(archive_name)
for target in targets:
    my_tarball.append(target)
my_tarball.gzip()

outfile = moveToXrootd(archive_name + '.gz', output_dir)
pipeline.setVariable('tarball_name', outfile)
