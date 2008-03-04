"""
@brief Script to drive setup the environment for driving the DRP
monitoring tasks.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os, shutil

drpRoot = lambda x : os.path.join(os.environ['DRPMONITORINGROOT'], x)

def find_par_file(filename):
    if not os.path.isfile(filename):
        shutil.copy(drpRoot(filename), filename)

find_par_file('rois.txt')
find_par_file('drp_pars.txt')

rootdir = os.getcwd()
os.environ['OUTPUTDIR'] = rootdir
os.environ['PIPELINESERVER'] = 'PROD'

from createDrpStreams import *

#for i in range(1, 29):
for i in range(1, 2):
    day = 'day%02i' % i
    print day
    try:
        os.mkdir(day)
    except OSError:
        pass
    os.system('chmod 777 %s ' % day)
    output_dir = os.path.abspath(day)
    os.system('cp rois.txt %s' % day)
    os.system('cp drp_pars.txt %s' % day)

    #drpStreams(daynum=i, output_dir=output_dir, debug=False)
    #
    # For development, restrict the number of ROIs to consider, i.e.,
    # just do the first.  This can also be controlled by commenting
    # out entries in rois.txt
    #
    drpStreams(daynum=i, output_dir=output_dir, debug=False, num_RoIs=1)
    os.chdir(rootdir)
