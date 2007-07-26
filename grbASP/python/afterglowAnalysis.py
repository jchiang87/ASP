"""
@brief Perform Unbinned Likelihood analysis on GRB afterglow data.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from parfile_parser import Parfile
from UnbinnedAnalysis import *

os.chdir(os.environ['OUTPUTDIR'])
grbName = Parfile(os.environ['GRBPARS'])['name']

afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

obs = UnbinnedObs(pars['ft1File'], pars['ft2File'], expMap=pars['expmap'],
                  expCube=pars['expcube'], irfs='DC2')

like = UnbinnedAnalysis(obs, grbName + '_afterglow_model.xml', 'Minuit')

like.thaw(6)

like.fit()

print like.model
print 'TS value: ', like.Ts(grbName)

like.writeXml()

os.system('chmod 777 *')
