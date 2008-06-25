"""
@brief Read the DIFFUSESOURCES db table and compute diffuse response
columns for the diffuse emission components.

@author J. Carson <carson@slac.stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from GtApp import GtApp
import readXml
from parfile_parser import Parfile
from drpDbAccess import findDiffuseSources

debug = True

os.chdir(os.environ['OUTPUTDIR'])

pars = Parfile('drp_pars.txt')

srcModel = readXml.SourceModel()
diffuseSources = findDiffuseSources()
print "Including the following sources from the DiffuseSources db table:"
for item in diffuseSources:
    print item
    srcModel[item] = readXml.Source(diffuseSources[item].domElement())
#
# @todo Verify that the following is not necessary:
#
srcModel['Galactic Diffuse'].spectrum.Value.free = 1
srcModel['Extragalactic Diffuse'].spectrum.Prefactor.free = 1
srcModel.filename = 'diffuse_model.xml'
srcModel.writeTo()

gtdiffresp = GtApp('gtdiffrsp')
gtdiffresp['evfile'] = pars['ft1file']
gtdiffresp['scfile'] = pars['ft2file']
gtdiffresp['irfs'] = pars['rspfunc']
gtdiffresp['srcmdl'] = srcModel.filename

if debug:
    print "Skipping the gtdiffresp command until it is parallelized."
    print "The needed diffuse response information will be computed in "
    print "sourceAnalysis.py"
    print gtdiffresp.command()
else:
    gtdiffresp.run()

os.system('chmod 777 *')
