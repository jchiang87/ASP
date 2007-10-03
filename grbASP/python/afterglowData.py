"""
@brief Extract data files for a GRB afterglow analysis.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
from GtApp import GtApp
#from getL1Data import getL1Data
from getFitsData import getFitsData
from ft1merge import ft1merge
from parfile_parser import Parfile
import readXml
import xmlSrcLib
import FuncFactory

gtselect = GtApp('gtselect', 'dataSubselector')
fmerge = GtApp('fmerge')

def getData(time, ra, dec, srcName, ft1, duration=5*3600, radius=15,
            extracted=False):
    ft1Merged = 'FT1_merged.fits'
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
    srcModel.filename = srcName + '_afterglow_model.xml'
    srcModel.writeTo()

    fmerge['infiles'] = '@Ft2FileList'
    fmerge['outfile'] = 'FT2_merged.fits'
    fmerge['clobber'] = 'yes'
    fmerge['columns'] = '" "'
    fmerge['mextname'] = '" "'
    fmerge['lastkey'] = '" "'
    fmerge.run()

    return srcModel, gtselect['outfile'], fmerge['outfile']

def afterglow_pars(infile):
    pars = Parfile(infile)
    return pars['name'], pars['ra'], pars['dec'], pars['tstart'], pars['tstop']

if __name__ == '__main__':
    import os, sys, shutil
    ft1, ft2 = getFitsData()
    outputDir = os.environ['OUTPUTDIR']
    os.chdir(outputDir)
    grbName, ra, dec, tstart, tstop = afterglow_pars(os.environ['GRBPARS'])

    srcModel, ft1, ft2 = getData(tstop, ra, dec, grbName, ft1)
    outfile = open('%s_afterglow_files' % grbName, 'w')
    outfile.write('ft1File = %s\n' % ft1)
    outfile.write('ft2File = %s\n' % ft2)
    outfile.write('xmlFile = %s\n' % srcModel.filename)
    outfile.close()

    os.system('chmod 777 *')
