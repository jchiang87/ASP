"""
@brief GRB Afterglow analysis development
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
from GtApp import GtApp
from getL1Data import getL1Data
from ft1merge import ft1merge
import readXml
import xmlSrcLib
import FuncFactory

gtselect = GtApp('gtselect')

def getData(time, ra, dec, srcName, duration=5*3600, radius=15,
            extracted=False):
    ft1Merged = 'FT1_merged.fits'
    ft1, ft2 = getL1Data(time, time + duration)
    if not extracted:
        ft1merge(ft1, ft1Merged)
    
    gtselect['infile'] =  ft1Merged
    gtselect['outfile'] = srcName + '_L1.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = time
    gtselect['tmax'] = time + duration
    gtselect['emin'] = 30
    gtselect['emax'] = 2e5
    gtselect['eventClass'] = -1
    if not extracted:
        gtselect.run()

    srcModel = readXml.SourceModel()
    GalProp = readXml.Source(xmlSrcLib.GalProp())
    EGDiffuse = readXml.Source(xmlSrcLib.EGDiffuse())
    srcModel['Galactic Diffuse'] = GalProp
    srcModel['Galactic Diffuse'].name = 'Galactic Diffuse'
    srcModel['Extragalactic Diffuse'] = EGDiffuse

    srcModel[srcName] = FuncFactory.PtSrc()
    srcModel[srcName].name = srcName
    srcModel[srcName].spatialModel.RA.value = ra
    srcModel[srcName].spatialModel.DEC.value = dec
    srcModel[srcName].spatialModel.setAttributes()
    srcModel.writeTo(srcName + '_model.xml')
    return srcModel, gtselect['outfile'], ft2[0]

if __name__ == '__main__':
    grbName = 'GRB080104514'
    srcModel, ft1, ft2 = getData(221142033.593, 57.5685, 15.7564, grbName,
                                 extracted=True)
    
    gtlivetimecube = GtApp('gtlivetimecube')
    gtlivetimecube['evfile'] = ft1
    gtlivetimecube['scfile'] = ft2
    gtlivetimecube['outfile'] = 'expCube_' + grbName + '.fits'
#    gtlivetimecube.run()
    
    gtexpmap = GtApp('gtexpmap')
    gtexpmap['evfile'] = ft1
    gtexpmap['scfile'] = ft2
    gtexpmap['exposure_cube_file'] = gtlivetimecube['outfile']
    gtexpmap['outfile'] = 'expmap_' + grbName + '.fits'
    gtexpmap['source_region_radius'] = 25
    gtexpmap['rspfunc'] = 'DSS'
#    gtexpmap.run()

    from UnbinnedAnalysis import *
    obs = UnbinnedObs(ft1, ft2, expMap=gtexpmap['outfile'],
                      expCube=gtlivetimecube['outfile'], irfs='DC2')
    like = UnbinnedAnalysis(obs, grbName + '_model.xml', 'NewMinuit')
    like.fit()
