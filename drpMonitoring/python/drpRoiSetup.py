"""
@brief Common setup for DRP region-of-interest analyses starting from
the directory given in the OUTPUTDIR environment variable.  Importing
this at the top of a script will set the cwd to the OUTPUTDIR and
make available the parameters in drp_pars.txt and rois.txt
after the getIntervalData.py script has been run.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from parfile_parser import Parfile
from read_data import read_data

class RoI(object):
    def __init__(self, region, ra, dec, radius, sourcerad):
        """The region name is constructed using self.name =
        'region%03i' % int(region)
        """
        self.id = int(region)
        self.name = 'region%03i' % self.id
        self.ra, self.dec, self.radius, self.sourcerad = (ra, dec, radius,
                                                          sourcerad)
        
class RoiDict(dict):
    def __init__(self, roiFile='rois.txt'):
        dict.__init__(self)
        for reg, ra, dec, radius, sourcerad in zip(*read_data(roiFile)):
            id = int(reg)
            self[id] = RoI(reg, ra, dec, radius, sourcerad)

output_dir = os.environ['OUTPUTDIR']
os.chdir(output_dir)

rootpath = lambda x : os.path.join(output_dir, x)
pars = Parfile('drp_pars.txt')
rois = RoiDict()

def currentRoi():
    id = int(os.environ['ROI_ID'])
    return rois[id]

