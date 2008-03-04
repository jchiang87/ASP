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

gtselect = GtApp('gtselect', 'dataSubselector')

_LatFt1File = '/nfs/farm/g/glast/u33/jchiang/DC2/FT1_merged_gti.fits'
_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

def LatGrbSpectrum(ra, dec=None, tmin=None, tmax=None, name=None, radius=15,
                   ft1File=_LatFt1File, ft2File=_LatFt2File):
    try:
        gbmNotice = ra
        ra = gbmNotice.ra
        dec = gbmNotice.dec
        tmin = gbmNotice.tmin
        tmax = gbmNotice.tmax
        name = gbmNotice.Name
    except AttributeError:
        pass

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
    like.writeCountsSpectra(name + '_prompt_spectra.fits')
    return like

def grbCoords(gbmNotice):
    infile = open(gbmNotice.Name + '_findSrc.txt')
    lines = infile.readlines()
    tokens = lines[-3].split()
    ra = float(tokens[0])
    dec = float(tokens[1])
    return ra, dec

def grbTiming(gbmNotice):
    from FitsNTuple import FitsNTuple
    gtis = FitsNTuple(gbmNotice.Name + '_LAT_2.fits', 'GTI')
    return gtis.START[0], gtis.STOP[-1]

def grbFiles(gbmNotice):
    infile = open(gbmNotice.Name + '_files')
    lines = infile.readlines()
    return 'FT1_merged.fits', lines[-1].strip()

if __name__ == '__main__':
    import os
    from GcnNotice import GcnNotice
    os.chdir(os.environ['OUTPUTDIR'])
    gbmNotice = GcnNotice(os.environ['GBMNOTICE'])
    ra, dec = grbCoords(gbmNotice)
    tmin, tmax = grbTiming(gbmNotice)
    ft1File, ft2File = grbFiles(gbmNotice)
    like = LatGrbSpectrum(ra, dec, tmin, tmax, gbmNotice.Name,
                          radius=15, ft1File=ft1File, ft2File=ft2File)

    os.system('chmod 777 *')
