"""
@brief Retrieve RoI-specific data.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
import drpDbAccess
from combineExpMaps import writeExpMapBounds
from parfile_parser import Parfile
from drpRoiSetup import rootpath, pars, rois

debug = False
#debug = True

id = int(os.environ['ROI_ID']) - 1  # This env var is set in DRP_monitoring.xml
name = rois[id].name
ra = rois[id].ra
dec = rois[id].dec
radius = rois[id].radius
sourcerad = rois[id].sourcerad
    
#
# Create the region subdirectory and cd to it.
#
try:
    os.mkdir(name)
except OSError:
    pass
os.chmod(name, 0777)
os.chdir(name)

#
# Extract events for this region.
#
gtselect = GtApp('gtselect')
gtselect['infile'] = rootpath(pars['ft1file'])
gtselect['outfile'] = name + '_events.fits'
gtselect['ra'] = ra
gtselect['dec'] = dec
gtselect['rad'] = radius
gtselect['emin'] = 30
gtselect['emax'] = 2e5
if debug:
    print gtselect.command()
else:
    gtselect.run()

#
# Access the SourceMonitoring db tables to build the source model for this ROI
#
drpDbAccess.buildXmlModel(ra, dec, sourcerad, name + '_model.xml')

#
# Write gtexpmap.par file for subsequent exposureMap.py calculations.
#
gtexpmap = GtApp('gtexpmap')
gtexpmap['evfile'] = gtselect['outfile']
gtexpmap['scfile'] = pars['ft2file']
gtexpmap['expcube'] = rootpath(pars['expCube'])
gtexpmap['outfile'] = 'expMap_' + name + '.fits'
gtexpmap['srcrad'] = sourcerad
gtexpmap['irfs'] = pars['rspfunc']
gtexpmap.pars.write('gtexpmap.par')

#
# Compute the exposure map in one chunk:
#
writeExpMapBounds(gtexpmap, nx=1, ny=1)

os.system('chmod 777 *')
