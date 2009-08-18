"""
@brief Extract data files for a GRB afterglow analysis.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, sys
from GtApp import GtApp
from getFitsData import getStagedFitsData
from ft1merge import ft1merge, ft2merge
from parfile_parser import Parfile
import readXml
import xmlSrcLib
import FuncFactory
import dbAccess

gtselect = GtApp('gtselect', 'dataSubselector')
fcopy = GtApp('fcopy')

def getData(time, ra, dec, srcName, ft1, ft2, duration=5*3600, radius=15,
            FT1_filter=None):
    ft1Merged = 'FT1_merged.fits'
    ft1merge(ft1, ft1Merged)

    ft2Merged = 'FT2_merged.fits'
    ft2merge(ft2, ft2Merged)

    if FT1_filter is not None:
        fcopy.run(infile=ft1Merged + '[%s]' % FT1_filter, 
                  outfile='!FT1_filtered.fits')
        gtselect['infile'] = fcopy['outfile'].strip('!')
    else:
        gtselect['infile'] =  ft1Merged

    gtselect['outfile'] = srcName + '_L1.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = time
    gtselect['tmax'] = time + duration
    gtselect['emin'] = 100
    gtselect['emax'] = 3e5
    gtselect['zmax'] = 100
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
    srcModel[srcName].spectrum.LowerLimit.value = 100
    srcModel[srcName].spectrum.UpperLimit.max = 5e5
    srcModel[srcName].spectrum.UpperLimit.value = 3e5
    srcModel.filename = srcName + '_afterglow_model.xml'
    srcModel.writeTo()

    return srcModel, gtselect['outfile'], ft2Merged

def afterglow_pars(infile):
    pars = Parfile(infile)
    return pars['name'], pars['ra'], pars['dec'], pars['tstart'], pars['tstop']

def updateProcessingLevel(name):
    sql = "select GRB_ID from GRB where GCN_NAME = '%s'" % name
    print sql
    def cursorFunc(cursor):
        for item in cursor:
            return item[0]
    grb_id = dbAccess.apply(sql, cursorFunc)
    print "grb_id = ", grb_id
    dbAccess.updateGrb(grb_id, ASP_PROCESSING_LEVEL=2)

if __name__ == '__main__':
    import os, sys, shutil
    from GrbAspConfig import grbAspConfig, irf_config
    from FileStager import FileStager

    outputDir = os.environ['OUTPUTDIR']

    fileStager = FileStager('stagingDir', stageArea=outputDir, 
                            messageLevel="INFO")
    ft1, ft2 = getStagedFitsData(fileStager=fileStager)

    os.chdir(outputDir)
    grbName, ra, dec, tstart, tstop = afterglow_pars(os.environ['GRBPARS'])
    updateProcessingLevel(grbName)

    config = grbAspConfig.find(tstart)
    print config

    irfs, ft1_filter = irf_config(tstart)
    print "irfs = ", irfs
    print "ft1_filter = ", ft1_filter

    srcModel, ft1, ft2 = getData(tstop, ra, dec, grbName, ft1, ft2,
                                 duration=config.AGTIMESCALE,
                                 radius=config.AGRADIUS,
                                 FT1_filter=ft1_filter)
    outfile = open('%s_afterglow_files' % grbName, 'w')
    outfile.write('ft1File = %s\n' % ft1)
    outfile.write('ft2File = %s\n' % ft2)
    outfile.write('xmlFile = %s\n' % srcModel.filename)
    outfile.close()

    os.system('chmod 777 *')
