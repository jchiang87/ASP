"""
@brief Common setup for DRP region-of-interest analyses starting from
the directory given in the output_dir environment variable.  Importing
this at the top of a script will set the cwd to the output_dir and
make available the parameters in drp_pars.txt and ROI db tables
after the getIntervalData.py script has been run.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
from parfile_parser import Parfile
#from read_data import read_data
import drpDbAccess

#_roiFile = os.path.join(os.environ['DRPMONITORINGROOT'], 'data', 'rois.txt')

class RoI(object):
    def __init__(self, region, ra, dec, radius, sourcerad):
        """The region name is constructed using self.name =
        'region%03i' % int(region)
        """
        self.name = 'region%03i' % int(region)
        self.ra, self.dec, self.radius, self.sourcerad = (ra, dec, radius,
                                                          sourcerad)
        
#class RoiList(list):
#    def __init__(self, roiFile=_roiFile):
#        for reg, ra, dec, radius, sourcerad in zip(*read_data(roiFile)):
#            self.append(RoI(reg, ra, dec, radius, sourcerad))

class RoiList(list):
    def __init__(self):
        sql = "select * from SOURCEMONITORINGROI"
        def cursorFunc(cursor):
            roi_dict = {}
            for entry in cursor:
                id, ra, dec, radius = [x for x in entry]
                roi_dict[id] = RoI(id, ra, dec, radius, radius+5)
            return roi_dict
        my_dict = drpDbAccess.apply(sql, cursorFunc)
        for i in range(1, len(my_dict) + 1):
            self.append(my_dict[i])

output_dir = os.environ['output_dir']
os.chdir(output_dir)

rootpath = lambda x : os.path.join(output_dir, x)
pars = Parfile('drp_pars.txt')
#rois = RoiList(pars['RoI_file'])
rois = RoiList()
