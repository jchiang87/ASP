"""
@brief Delete interim files from nfs workspace

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import glob

output_dir = os.environ['OUTPUTDIR']

os.chdir(output_dir)

suffix = os.getcwd().split('/')[-1]
saved = ('Filtered_evt_%s.fits' % suffix,
         'Filtered_evt_map_%s.fits' % suffix,
         'Filtered_evt_map_%s.list' % suffix, 
         'Filtered_evt_map_%s.reg' % suffix, 
         'Filtered_evt_map_pgw_out_%s.fits' % suffix, 
         'Filtered_evt_map_ait_%s.gif' % suffix, 
         'FT2_%s.fits' % suffix)

targets = glob.glob('*')

for target in targets:
    if target not in saved:
        os.system('rm -f %s' % target)
