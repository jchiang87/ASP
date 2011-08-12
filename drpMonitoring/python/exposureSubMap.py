"""
@brief Run gtexpmap for specified submaps to be run in parallel.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
from combineExpMaps import readExpMapBounds

def exposureSubMap(outputDir, debug=False):
    os.chdir(outputDir)
    bounds = readExpMapBounds()

# create a subdirectory to hold gtexpmap.par to avoid collisions with
# other getexp processes being run in parallel
    submap = int(os.environ['EXPMAP_ID'])
    try:
        submap_dir = 'gtexpmap_subdir_%02i' % submap
        os.mkdir(submap_dir)
        os.chmod(submap_dir, 0777)
    except OSError:
        if os.path.isdir(submap_dir):
            os.chmod(submap_dir, 0777)
        else:
            raise OSError, "Error creating directory: " + submap_dir
    pfiles = os.environ['PFILES'].split(';')
    os.environ['PFILES'] = submap_dir + ';' + pfiles[1]
    os.system('cp gtexpmap.par %s' % submap_dir)

# Account for off-by-one error in how jobs can be numbered in P-II xml code.
    map_id = int(os.environ["EXPMAP_ID"]) - 1  

    gtexpmap = GtApp('gtexpmap')
    gtexpmap['outfile'] = bounds[map_id].filename
    gtexpmap['submap'] = 'yes'
    gtexpmap['nlongmin'] = bounds[map_id].xmin
    gtexpmap['nlongmax'] = bounds[map_id].xmax
    gtexpmap['nlatmin'] = bounds[map_id].ymin
    gtexpmap['nlatmax'] = bounds[map_id].ymax

    if debug:
        print gtexpmap.command()
    else:
        gtexpmap.run()

    os.system('chmod 777 *')

if __name__ == '__main__':
    pass
## include this code for backwards compatibility    
#    from drpRoiSetup import currentRoi
#    roi = currentRoi()
#    outputDir = roi.name
#    exposureSubMap(outputDir, debug=False)
    
