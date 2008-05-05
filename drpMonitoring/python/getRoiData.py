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
from combineExpMaps import writeExpMapBounds
from parfile_parser import Parfile
from search_Srcs import search_Srcs
import readXml
from drpRoiSetup import rootpath, pars, currentRoi

debug = False
#debug = True

roi = currentRoi()
name = roi.name
ra = roi.ra
dec = roi.dec
radius = roi.radius
sourcerad = roi.sourcerad
zenmax = pars['zenmax']
    
#
# Create the region subdirectory and cd to it.
#
try:
    os.mkdir(name)
except OSError:
    pass
#os.chmod(name, 0777)
os.chdir(name)

#
# Extract events for this region.
#
gtselect = GtApp('gtselect')
gtselect['infile'] = rootpath(pars['ft1file'])
gtselect['outfile'] = name + '_events_no_zen.fits'
gtselect['ra'] = ra
gtselect['dec'] = dec
gtselect['rad'] = radius
gtselect['emin'] = 30
gtselect['emax'] = 3e5
gtselect['tmin'] = pars['start_time']
gtselect['tmax'] = pars['stop_time']
if debug:
    print gtselect.command()
else:
    gtselect.run()

#
# apply ROI-dependent zenith angle cut
#
gtmktime = GtApp('gtmktime')
gtmktime['evfile'] = gtselect['outfile']
gtmktime['outfile'] = name + '_events.fits'
gtmktime['scfile'] = pars['ft2file']
gtmktime['filter'] = 'angsep(RA_ZENITH,DEC_ZENITH,%f,%f)+%f<%i' % (ra, dec,
                                                                   radius,
                                                                   zenmax)
if debug:
    print gtmktime.command()
else:
    gtmktime.run()

#
# Because of custom GTI cuts, need to run gtltcube for each ROI.
#
gtltcube = GtApp('gtltcube')
gtltcube.run(evfile=gtmktime['outfile'], scfile=pars['ft2file'],
             outfile=pars['expCube'])

#
# Build the xml model by using the point source model derived in
# sourceSelection process
#
sourceModel = rootpath('point_sources.xml')
#modelRequest = 'dist((RA,DEC),(%f,%f))<%e' % (ra, dec, sourcerad)
modelRequest = 'dist((RA,DEC),(%f,%f))<%e' % (ra, dec, radius)
outputModel = name + '_ptsrcs_model.xml'
search_Srcs(sourceModel, modelRequest, outputModel)

srcModel = readXml.SourceModel(outputModel)

diffModel = readXml.SourceModel(rootpath('diffuse_model.xml'))
for item in diffModel.names():
    print item
    srcModel[item] = diffModel[item]

srcModel.filename = name + '_model.xml'
srcModel.writeTo()

#
# Write gtexpmap.par file for subsequent exposureMap.py calculations.
#
gtexpmap = GtApp('gtexpmap')
gtexpmap['evfile'] = gtmktime['outfile']
gtexpmap['scfile'] = pars['ft2file']
gtexpmap['expcube'] = pars['expCube']
gtexpmap['outfile'] = 'expMap_' + name + '.fits'
gtexpmap['srcrad'] = sourcerad
gtexpmap['irfs'] = pars['rspfunc']
gtexpmap.pars.write('gtexpmap.par')

#
# Compute the exposure map in one chunk:
#
writeExpMapBounds(gtexpmap, nx=1, ny=1)

os.system('chmod 777 *')
