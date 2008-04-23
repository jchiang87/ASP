"""
@brief Extract GRB data for a given position on the sky and a given
time range, and perform a simple power-law fit, saving the result in
an XML model file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import sys, os
import numpy as num
from GtApp import GtApp
import readXml
import FuncFactory as funcFactory
from refinePosition import absFilePath
from UnbinnedAnalysis import *
import dbAccess

gtselect = GtApp('gtselect', 'dataSubselector')
gtlike = GtApp('gtlike', 'Likelihood')

def pl_integral(emin, emax, gamma):
    if gamma == 1:
        return num.log(emax/emin)
    else:
        return (emax**(1.-gamma) - emin**(1.-gamma))/(1. - gamma)

def pl_energy_flux(like, emin, emax, srcname="point source 0"):
    """compute energy flux (ergs/s/cm^2) over the desired energy
    range for a power-law source.
    """
    ergperMeV = 1.602e-6
    spec = like[srcname].src.spectrum()
    gamma = -spec.getParam('Index').getTrueValue()
    flux = (pl_integral(emin, emax, gamma-1)/pl_integral(emin, emax, gamma)
            *like[srcname].flux(emin, emax)*ergperMeV)
    fractionalError = (spec.getParam('Integral').error()
                       /spec.getParam('Integral').getValue())
    return flux, flux*fractionalError

def LatGrbSpectrum(ra, dec=None, tmin=None, tmax=None, name=None, radius=15,
                   ft1File=None, ft2File=None, irfs='DC2',
                   optimizer='Minuit'):
    try:
        gcnNotice = ra
        ra = gcnNotice.ra
        dec = gcnNotice.dec
        tmin = gcnNotice.tmin
        tmax = gcnNotice.tmax
        name = gcnNotice.Name
    except AttributeError:
        pass

    gtselect['infile'] = ft1File
    gtselect['outfile'] = name + '_LAT_3.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = tmin
    gtselect['tmax'] = tmax
    gtselect['zmax'] = 100
    gtselect.run()

    src = funcFactory.PtSrc()
    src.spectrum.Integral.min = 0
    src.spectrum.Integral.max = 1e7
    src.spectrum.setAttributes()
    src.spatialModel.RA.value = ra
    src.spatialModel.DEC.value = dec
    src.spatialModel.setAttributes()
    srcModel = readXml.SourceModel()
    srcModel[name] = src
    srcModelFile = name + '_model.xml'
    srcModel.writeTo(srcModelFile)

    spectrumFile = name + '_grb_spec.fits'

    if irfs == 'DSS':
        irfs = 'DC2'
    obs = UnbinnedObs(gtselect['outfile'], ft2File, expMap=None,
                      expCube=None, irfs=irfs)
    like = UnbinnedAnalysis(obs, srcModelFile, optimizer)
    like[0].setBounds(0, 1e7)
    like.fit()
    like.writeXml()
    like.writeCountsSpectra(spectrumFile)

    grb_id = int(os.environ['GRB_ID'])

    f30 = pl_energy_flux(like, 30, 3e5)
    fluence_30, f30_error = f30[0]*(tmax - tmin), f30[1]*(tmax - tmin)
    f100 = pl_energy_flux(like, 100, 3e5)
    fluence_100, f100_error = f100[0]*(tmax - tmin), f100[1]*(tmax - tmin)
    dbAccess.updateGrb(grb_id, SPECTRUMFILE="'%s'" % absFilePath(spectrumFile),
                       XML_FILE="'%s'" % absFilePath(srcModelFile),
                       PHOTON_INDEX=like[1].getTrueValue(),
                       PHOTON_INDEX_ERROR=like[1].error(),
                       FLUENCE_30=fluence_30, FLUENCE_30_ERROR=f30_error,
                       FLUENCE_100=fluence_100, FLUENCE_100_ERROR=f100_error)
    return like

def grbCoords(gcnNotice):
    infile = open(gcnNotice.Name + '_findSrc.txt')
    lines = infile.readlines()
    tokens = lines[-3].split()
    ra = float(tokens[0])
    dec = float(tokens[1])
    return ra, dec

def grbTiming(gcnNotice):
    from FitsNTuple import FitsNTuple
    gtis = FitsNTuple(gcnNotice.Name + '_LAT_2.fits', 'GTI')
    return gtis.START[0], gtis.STOP[-1]

def grbFiles(gcnNotice):
    infile = open(gcnNotice.Name + '_files')
    lines = infile.readlines()
    return 'FT1_merged.fits', lines[-1].strip()

if __name__ == '__main__':
    import os
    from GcnNotice import GcnNotice
    from GrbAspConfig import grbAspConfig

    os.chdir(os.environ['OUTPUTDIR'])
    gcnNotice = GcnNotice(int(os.environ['GRB_ID']))
    
    config = grbAspConfig.find(gcnNotice.start_time)
    print config

    ra, dec = grbCoords(gcnNotice)
    tmin, tmax = grbTiming(gcnNotice)
    ft1File, ft2File = grbFiles(gcnNotice)
    like = LatGrbSpectrum(ra, dec, tmin, tmax, gcnNotice.Name,
                          ft1File=ft1File, ft2File=ft2File,
                          radius=config.RADIUS, 
                          irfs=config.IRFS,
                          optimizer=config.OPTIMIZER)

    os.system('chmod 777 *')
