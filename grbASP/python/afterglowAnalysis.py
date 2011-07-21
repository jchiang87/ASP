"""
@brief Perform Unbinned Likelihood analysis on GRB afterglow data.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
from parfile_parser import Parfile
from UnbinnedAnalysis import *
from GrbAspConfig import grbAspConfig, irf_config
import dbAccess
import pyfits
from pass_version import pass_version

def absFilePath(filename):
    abspath = os.path.abspath(filename)
    try:
        return os.path.join('/nfs/farm/g/glast', abspath.split('g.glast.')[1])
    except IndexError:
        return abspath

os.chdir(os.environ['OUTPUTDIR'])
grbpars = Parfile(os.environ['GRBPARS'])

config = grbAspConfig.find(grbpars['tstart'])
print config

#irfs = config.IRFS
#if irfs == 'DSS':
#    irfs = 'DC2'
irfs, ft1_filter = irf_config(grbpars['tstart'])

grbName = grbpars['name']
afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

print "Using files: "
print pars

#
# Perform Likelihood analysis
#
print "Running unbinned analysis..."
obs = UnbinnedObs(pars['ft1File'], pars['ft2File'], expMap=pars['expmap'],
                  expCube=pars['expcube'], irfs=irfs)

sys.stdout.flush()
print "Creating UnbinnedAnalysis object..."
like = UnbinnedAnalysis(obs, grbName + '_afterglow_model.xml', config.OPTIMIZER)

sys.stdout.flush()
print "likelihood state:"
like.state()

try:
    like.fit()
except:
    try:
        like.fit()
    except:
        pass

print like.model

TS_value = like.Ts(grbName)

print 'TS value: ', TS_value

like.writeXml()
spectrumFile = grbName + '_afterglow_spec.fits'
like.writeCountsSpectra(spectrumFile)
like.state(open(grbName + '_afterglow_analysis.py', 'w'))

grb_id = int(os.path.basename(os.getcwd()))

try:
    dbAccess.insertAfterglow(grb_id)
except dbAccess.cx_Oracle.IntegrityError, message:
    print message

flux = like[grbName].funcs['Spectrum'].params['Integral'].value()
fluxerr = like[grbName].funcs['Spectrum'].params['Integral'].parameter.error()

index = like[grbName].funcs['Spectrum'].params['Index'].value()
indexerr = like[grbName].funcs['Spectrum'].params['Index'].parameter.error()

ra = like[grbName].funcs['Position'].params['RA'].value()
dec = like[grbName].funcs['Position'].params['DEC'].value()

xmlfile = absFilePath(like.srcModel)

ft1 = pyfits.open(pars['ft1File'])
tstart = ft1[0].header['TSTART']
tstop = ft1[0].header['TSTOP']

dbAccess.updateAfterglow(grb_id, FLUX=flux, FLUX_ERROR=fluxerr,
                         PHOTON_INDEX=index, PHOTON_INDEX_ERROR=indexerr,
                         LAT_RA=ra, LAT_DEC=dec, XML_FILE="'%s'" % xmlfile,
                         SPECTRUMFILE="'%s'" % absFilePath(spectrumFile), 
                         LAT_FIRST_TIME=tstart, LAT_LAST_TIME=tstop)

#
# import GtApp here since it imports py_facilities which does not
# interact happily with pyLikelihood and causes core dumps.
#
from GtApp import GtApp

#
# Compute a simple light curve
#
gtselect = GtApp('gtselect')
if pass_version(pars['ft1File']) != 'NONE':
    gtselect['evclass'] = 0
gtselect.run(evfile=pars['ft1File'], outfile='filtered_3deg.fits',
             ra=grbpars['ra'], dec=grbpars['dec'], rad=3, coordSys='CEL',
             emin=100, emax=3e5)

gtbin = GtApp('gtbin')
gtbin.run(evfile=gtselect['outfile'], scfile=pars['ft2File'], 
          outfile=grbName + '_afterglow_lc.fits',
          algorithm='LC', tbinalg='LIN', tstart=grbpars['tstop'],
          tstop=grbpars['tstop'] + config.AGTIMESCALE, 
          dtime=config.AGTIMESCALE/100)

gtexposure = GtApp('gtexposure')
gtexposure.run(infile=gtbin['outfile'], scfile=pars['ft2File'],
               irfs=config.IRFS, srcmdl=like.srcModel,
               target=grbName, emin=100, emax=3e5)

dbAccess.updateAfterglow(grb_id, 
                         LIGHTCURVEFILE= "'%s'" % absFilePath(gtbin['outfile']))
                                         
os.system('chmod 777 *')
