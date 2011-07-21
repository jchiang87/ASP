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
import pyfits
from GtApp import GtApp
import readXml
import xmlSrcLib
import FuncFactory as funcFactory
from refinePosition import absFilePath, likelyUL
from UnbinnedAnalysis import *
import dbAccess
from parfile_parser import Parfile
from FitsNTuple import FitsNTuple, FitsNTupleError
from addNdifrsp import addNdifrsp
import pipeline
from pass_version import pass_version

gtselect = GtApp('gtselect', 'dataSubselector')
gtlike = GtApp('gtlike', 'Likelihood')
gtexpmap = GtApp('gtexpmap', 'Likelihood')
gtdiffrsp = GtApp('gtdiffrsp', 'Likelihood')

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

def pl_fluence(like, emin, emax, srcname, tmin, tmax):
    flux = pl_energy_flux(like, emin, emax, srcname)
    return flux[0]*(tmax - tmin), flux[1]*(tmax - tmin)

def createExpMap(ft1File, ft2File, name, config):
    gtexpmap.run(evfile=ft1File, scfile=ft2File, expcube="none",
                 outfile='%s_expMap.fits' % name, irfs=config.IRFS,
                 srcrad=config.RADIUS+10)
    return gtexpmap['outfile']

class ZeroFt1EventsError(StandardError):
    "Zero events in FT1 file."

def LatGrbSpectrum(ra, dec, tmin, tmax, name, ft1File, ft2File, config):
    radius = config.RADIUS
    irfs = config.IRFS
    optimizer = config.OPTIMIZER
    expMap = None

    gtselect['infile'] = ft1File
    gtselect['outfile'] = name + '_LAT_3.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = tmin
    gtselect['tmax'] = tmax
    gtselect['emin'] = 100
    gtselect['emax'] = 3e5
    gtselect['zmax'] = 100
    if pass_version(ft1File) != 'NONE':
        gtselect['evclass'] = 0
    gtselect.run()

    events = pyfits.open(gtselect['outfile'])
    if events['EVENTS'].size() == 0:
        raise ZeroFt1EventsError

    expMap = createExpMap(gtselect['outfile'], ft2File, name, config)
    #
    # Check if exposure is zero at this location
    #
    foo = pyLike.WcsMap2(expMap)
    grb_dir = pyLike.SkyDir(ra, dec)
    if foo(grb_dir) == 0:
        raise ZeroFt1EventsError

    src = funcFactory.PtSrc()
    src.spectrum.Integral.min = 0
    src.spectrum.Integral.max = 1e7
    src.spectrum.LowerLimit.value = 100.
    src.spectrum.setAttributes()
    src.spatialModel.RA.value = ra
    src.spatialModel.DEC.value = dec
    src.spatialModel.setAttributes()
    srcModel = readXml.SourceModel()
    srcModel[name] = src
    srcModel[name].name = name

    GalProp = readXml.Source(xmlSrcLib.GalProp())
    EGDiffuse = readXml.Source(xmlSrcLib.EGDiffuse())
    srcModel['Galactic Diffuse'] = GalProp
    srcModel['Galactic Diffuse'].name = 'Galactic Diffuse'
    srcModel['Extragalactic Diffuse'] = EGDiffuse
        
    srcModelFile = name + '_model.xml'
    srcModel.writeTo(srcModelFile)

    addNdifrsp(gtselect['outfile'])
    gtdiffrsp.run(evfile=gtselect['outfile'], scfile=ft2File, 
                  srcmdl=srcModelFile, irfs=config.IRFS)

    spectrumFile = name + '_grb_spec.fits'

    if irfs == 'DSS':
        irfs = 'DC2'
    obs = UnbinnedObs(gtselect['outfile'], ft2File, expMap=expMap,
                      expCube=None, irfs=irfs)
    like = UnbinnedAnalysis(obs, srcModelFile, optimizer)
    like[0].setBounds(0, 1e7)
    #
    # Another check for zero exposure.
    #
    if sum(like[name].src.exposure()) == 0:
        raise ZeroFt1EventsError

    like.fit()
    like.writeXml()
    like.writeCountsSpectra(spectrumFile)

    #
    # Write the predicted number of counts for the energy bins in the
    # GCN_Notice.tpl file.
    #
    pars = Parfile(name + '_pars.txt', fixed_keys=False)
    pars['GRB_INTEN1'] = like[name].Npred(100, 1e3)
    pars['GRB_INTEN2'] = like[name].Npred(1e3, 1e4)
#    pars['GRB_INTEN3'] = like[name].Npred(1e4, 2e5)
    pars['GRB_INTEN3'] = like[name].Npred(1e4, 1e5)
    pars.write()

    grb_id = int(os.environ['GRB_ID'])

    f30 = pl_fluence(like, 30, 3e5, name, tmin, tmax)
    f100 = pl_fluence(like, 1e2, 3e5, name, tmin, tmax)
    f1GeV = pl_fluence(like, 1e3, 3e5, name, tmin, tmax)
    f10GeV = pl_fluence(like, 1e4, 3e5, name, tmin, tmax)

    flux_par = like[name].funcs['Spectrum'].getParam('Integral')
    index_par = like[name].funcs['Spectrum'].getParam('Index')

    Ts = like.Ts(name)
    if Ts < 25:
        sys.path.insert(0, '.')
        from UpperLimits import UpperLimits
        ul = UpperLimits(like)
        upper_limit = ul[name].compute(renorm=True, emin=100, emax=3e5)
#        upper_limit = [like.flux(name, 100, 3e5) + like.fluxError(name, 100, 3e5), 0]
        dbAccess.updateGrb(grb_id, TS_VALUE=Ts, IS_UPPER_LIMIT=1)
        flux_value = upper_limit[0]
    else:
        dbAccess.updateGrb(grb_id, TS_VALUE=Ts, IS_UPPER_LIMIT=0)
        flux_value = flux_par.getTrueValue()

    dbAccess.updateGrb(grb_id, SPECTRUMFILE="'%s'" % absFilePath(spectrumFile),
                       XML_FILE="'%s'" % absFilePath(srcModelFile),
                       FT1_FILE="'%s'" % absFilePath(name + '_LAT_3.fits'),
                       PHOTON_INDEX=index_par.getTrueValue(),
                       PHOTON_INDEX_ERROR=index_par.error(),
                       FLUENCE_30=f30[0], FLUENCE_30_ERROR=f30[1],
                       FLUENCE_100=f100[0], FLUENCE_100_ERROR=f100[1],
                       FLUENCE_1GEV=f1GeV[0], FLUENCE_1GEV_ERROR=f1GeV[1],
                       FLUENCE_10GEV=f10GeV[0], FLUENCE_10GEV_ERROR=f10GeV[1],
                       FLUX=flux_par.getTrueValue(), 
                       FLUX_ERROR=flux_par.error()*flux_par.getScale(),
                       TS_VALUE=Ts)

    try:
        events = FitsNTuple(gtselect['outfile'])
    except FitsNTupleError:
        return None
    soft_counts = float(len(num.where(events.ENERGY <= 1e3)[0]))
    hard_counts = len(events.ENERGY) - soft_counts
    if soft_counts > 0:
        hardness_ratio = hard_counts/soft_counts
        dbAccess.updateGrb(grb_id, HARDNESS_RATIO=hardness_ratio)

    return like

def grbCoords(gcnNotice):
    pars = Parfile(gcnNotice.Name + '_pars.txt')
    return pars['ra'], pars['dec']

def grbTiming(gcnNotice):
    from FitsNTuple import FitsNTuple
    gtis = FitsNTuple(gcnNotice.Name + '_LAT_2.fits', 'GTI')
    return gtis.START[0], gtis.STOP[-1]

if __name__ == '__main__':
    import os
    from GcnNotice import GcnNotice
    from GrbAspConfig import grbAspConfig

    def grbFiles(gcnNotice):
        infile = open(gcnNotice.Name + '_files')
        lines = infile.readlines()
        return 'FT1_merged.fits', lines[-1].strip()

    os.chdir(os.environ['OUTPUTDIR'])

    grb_id = int(os.environ['GRB_ID'])
    gcnNotice = GcnNotice(grb_id, skipped=('FERMI_LAT_POSITION',))

    config = grbAspConfig.find(gcnNotice.start_time)
    print config

    ra, dec = grbCoords(gcnNotice)
    tmin, tmax = grbTiming(gcnNotice)
    ft1File, ft2File = grbFiles(gcnNotice)

    try:
        like = LatGrbSpectrum(ra, dec, tmin, tmax, gcnNotice.Name,
                              ft1File, ft2File, config)
    except ZeroFt1EventsError:
        pipeline.setVariable("skipDataProducts", "affirmed")
        
    os.system('chmod 777 *')
