"""
@brief Compute diffuse response columns for standard diffuse
emission components.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
import readXml
import xmlSrcLib
from parfile_parser import Parfile

debug = True

os.chdir(os.environ['OUTPUTDIR'])

pars = Parfile('drp_pars.txt')

srcModel = readXml.SourceModel()
GalProp = readXml.Source(xmlSrcLib.GalProp())
EGDiffuse = readXml.Source(xmlSrcLib.EGDiffuse())
srcModel['Galactic Diffuse'] = GalProp
srcModel['Galactic Diffuse'].name = 'Galactic Diffuse'
srcModel['Galactic Diffuse'].spectrum.Value.free = 1
srcModel['Extragalactic Diffuse'] = EGDiffuse
srcModel['Extragalactic Diffuse'].spectrum.Prefactor.free = 1
srcModel.filename = 'diffuse_model.xml'
srcModel.writeTo()

gtdiffresp = GtApp('gtdiffrsp')
gtdiffresp['evfile'] = pars['ft1file']
gtdiffresp['scfile'] = pars['ft2file']
gtdiffresp['irfs'] = pars['rspfunc']
gtdiffresp['srcmdl'] = srcModel.filename

if debug:
    print gtdiffresp.command()
else:
    gtdiffresp.run()

os.system('chmod 777 *')
