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

archive_name = 'PGW_%s_%s.tar' % tuple(os.getcwd().split('/')[-2:])

suffix = os.getcwd().split('/')[-1]

targets = ('Filtered_evt_%s.fits' % suffix, 
           'Filtered_evt_map_%s.fits' % suffix, 
           'Filtered_evt_map_%s.list' % suffix, 
           'Filtered_evt_map_%s.reg' % suffix, 
           'Filtered_evt_map_ait_%s.gif' % suffix, 
           'FT2_%s.fits' % suffix, 
           'Filtered_evt_map_old.list', 
           'updated_positions.txt', 
           'Filtered_evt_map_ait.fits')

my_tarball = TarBall(archive_name)
for target in targets:
    my_tarball.append(target)
my_tarball.gzip()

outfile = moveToXrootd(archive_name + '.gz', os.environ['OUTPUTDIR'])

pipeline.setVariable('tarball_name', outfile)
