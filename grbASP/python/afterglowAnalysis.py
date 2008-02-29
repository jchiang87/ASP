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
from GrbAspConfig import grbAspConfig
import dbAccess

os.chdir(os.environ['OUTPUTDIR'])
grbpars = Parfile(os.environ['GRBPARS'])

config = grbAspConfig.find(grbpars['tstart'])
print config

irfs = config.IRFS
if irfs == 'DSS':
    irfs = 'DC2'

grbName = grbpars['name']
afterglowFiles = grbName + '_afterglow_files'
pars = Parfile(afterglowFiles)

obs = UnbinnedObs(pars['ft1File'], pars['ft2File'], expMap=pars['expmap'],
                  expCube=pars['expcube'], irfs=irfs)

like = UnbinnedAnalysis(obs, grbName + '_afterglow_model.xml', config.OPTIMIZER)

like.thaw(6)

try:
    like.fit()
except:
    try:
        like.fit()
    except:
        pass

print like.model
print 'TS value: ', like.Ts(grbName)

sql = "select GRB_ID from GRB where GCN_NAME = '%s'" % grbName
def getId(cursor):
    for item in cursor:
        return item[0]
    
grb_id = dbAccess.apply(sql, getId)

dbAccess.insertAfterglow(grb_id)

flux = like[grbName].flux(100, 3e5)
flux


like.writeXml()

os.system('chmod 777 *')
