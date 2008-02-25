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

def getData(time, ra, dec, srcName, ft1, ft2, duration=5*3600, radius=15):
    ft1Merged = 'FT1_merged.fits'
    ft1merge(ft1, ft1Merged)

    ft2Merged = 'FT2_merged.fits'
    ft2merge(ft2, ft2Merged)

    gtselect['infile'] =  ft1Merged
    gtselect['outfile'] = srcName + '_L1.fits'
    gtselect['ra'] = ra
    gtselect['dec'] = dec
    gtselect['rad'] = radius
    gtselect['tmin'] = time
    gtselect['tmax'] = time + duration
#    gtselect['emin'] = 30
    gtselect['emin'] = 100
    gtselect['emax'] = 2e5
    gtselect['eventClass'] = -1
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
    srcModel.filename = srcName + '_afterglow_model.xml'
    srcModel.writeTo()

    return srcModel, gtselect['outfile'], ft2Merged

def afterglow_pars(infile):
    pars = Parfile(infile)
    return pars['name'], pars['ra'], pars['dec'], pars['tstart'], pars['tstop']

def updateAnalysisVersion(name):
    sql = "select * from GRB where GCN_NAME = '%s'" % name
    def cursorFunc(cursor):
        for item in cursor:
            return item[0]
    grb_id = dbAccess.apply(sql, cursorFunc)
    dbAccess.updateGrb(grb_id, ANALYSIS_VERSION=1)

if __name__ == '__main__':
    import os, sys, shutil
    from GrbAspConfig import grbAspConfig

    ft1, ft2 = getStagedFitsData()
    outputDir = os.environ['OUTPUTDIR']
    os.chdir(outputDir)
    grbName, ra, dec, tstart, tstop = afterglow_pars(os.environ['GRBPARS'])
    updateAnalysisVersion(grbName)

    config = grbAspConfig.find(tstart)
    print config

    srcModel, ft1, ft2 = getData(tstop, ra, dec, grbName, ft1, ft2,
                                 duration=config.AGTIMESCALE,
                                 radius=config.AGRADIUS)
    outfile = open('%s_afterglow_files' % grbName, 'w')
    outfile.write('ft1File = %s\n' % ft1)
    outfile.write('ft2File = %s\n' % ft2)
    outfile.write('xmlFile = %s\n' % srcModel.filename)
    outfile.close()

    os.system('chmod 777 *')
