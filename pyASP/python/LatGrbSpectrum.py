"""
@brief Extract GRB data for a given position on the sky and a given
time range, and perform a simple power-law fit, saving the result in
an XML model file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

from GtApp import GtApp
import readXml
import FuncFactory as funcFactory
from UnbinnedAnalysis import *

gtselect = GtApp('gtselect')

_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'
_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

def LatGrbSpectrum(ra, dec, tmin, tmax, name, radius=15,
                   ft1File=_LatFt1File, ft2File=_LatFt2File):
    gtselect['infile'] = ft1File
    gtselect['outfile'] = name + '_LAT_3.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = tmin
    gtselect['tmax'] = tmax
    gtselect.run()

    src = funcFactory.PtSrc()
    src.spatialModel.RA.value = ra
    src.spatialModel.DEC.value = dec
    src.spatialModel.setAttributes()
    srcModel = readXml.SourceModel()
    srcModel[name] = src
    srcModelFile = name + '_model.xml'
    srcModel.writeTo(srcModelFile)

    obs = UnbinnedObs(gtselect['outfile'], ft2File, expMap=None,
                      expCube=None, irfs='DC2')
    like = UnbinnedAnalysis(obs, srcModelFile, 'Minuit')
    like[0].setBounds(0, 1e7)
    like.fit()
    like.writeXml()
    return like

if __name__ == '__main__':
    like = LatGrbSpectrum(170.166, -13.316, 222367682.458, 222367682.60699999,
                          'GRB080118700')
