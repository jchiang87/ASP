"""
@brief Common setup for DRP region-of-interest analyses starting from
the directory given in the output_dir environment variable.  Importing
this at the top of a script will set the cwd to the output_dir and
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
        self.name = 'region%03i' % int(region)
        self.ra, self.dec, self.radius, self.sourcerad = (ra, dec, radius,
                                                          sourcerad)
        
class RoiList(list):
    def __init__(self, roiFile='rois.txt'):
        for reg, ra, dec, radius, sourcerad in zip(*read_data(roiFile)):
            self.append(RoI(reg, ra, dec, radius, sourcerad))

output_dir = os.environ['output_dir']
os.chdir(output_dir)

rootpath = lambda x : os.path.join(output_dir, x)
pars = Parfile('drp_pars.txt')
rois = RoiList()
