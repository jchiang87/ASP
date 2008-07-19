"""
@brief Delete interim files from nfs workspace

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import glob

targets = ('*.par', 'FT1_merged.fits', '*.xml', 'pgwaveFileList',
           '*rois.txt', '*filtered*.fits', 'drp_pars.txt')

for target in targets:
    os.system('rm -f %s' % target)

region_targets = ('events_*.fits',
                  '*.par',
                  '*.txt',
                  'expMap_region???_00.fits',
                  'region???_events_no_zen.fits',
                  'region???_model.xml_input',
                  'region???_ptsrcs_model.xml',
                  'gtexpmap_subdir_01')

regions = glob.glob('region???')

for region in regions:
    for item in region_targets:
        target = os.path.join(region, item)
        os.system('rm -rf %s' % target)
