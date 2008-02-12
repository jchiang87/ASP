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
import xmlSrcLib
from drpRoiSetup import rootpath, pars, rois

debug = False
#debug = True

id = int(os.environ['ROI_ID']) - 1  # This env var is set in DRP_monitoring.xml
name = rois[id].name
ra = rois[id].ra
dec = rois[id].dec
radius = rois[id].radius
sourcerad = rois[id].sourcerad
zenmax = pars['zenmax']
    
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
gtselect['outfile'] = name + '_events_no_zen.fits'
gtselect['ra'] = ra
gtselect['dec'] = dec
gtselect['rad'] = radius
gtselect['emin'] = 30
gtselect['emax'] = 2e5
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
# Because of custom GTI cuts, need to run gtltcube
#
gtltcube = GtApp('gtltcube')
gtltcube.run(evfile=gtmktime['outfile'], scfile=pars['ft2file'],
             outfile=pars['expCube'])

##
## Access the SourceMonitoring db tables to build the source model for this ROI
##
#drpDbAccess.buildXmlModel(ra, dec, sourcerad, name + '_model.xml')

#
# build the xml model by using the point source model derived in
# sourceSelection process
#
sourceModel = '../point_sources.xml'
modelRequest = 'dist((RA,DEC),(%f,%f))<%e' % (ra, dec, sourcerad)
outputModel = name + '_ptsrcs_model.xml'
model = search_Srcs(sourceModel, modelRequest, outputModel)

srcModel = readXml.SourceModel(outputModel)
GalProp = readXml.Source(xmlSrcLib.GalProp())
EGDiffuse = readXml.Source(xmlSrcLib.EGDiffuse())
srcModel['Galactic Diffuse'] = GalProp
srcModel['Galactic Diffuse'].name = 'Galactic Diffuse'
srcModel['Galactic Diffuse'].spectrum.Value.free = 1
srcModel['Extragalactic Diffuse'] = EGDiffuse
srcModel['Extragalactic Diffuse'].spectrum.Prefactor.free = 1
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
