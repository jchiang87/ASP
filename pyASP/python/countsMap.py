#!/usr/bin/env python

"""
@brief Make counts maps.

@author W. Focke <focke@slac.stanford.edu>
"""

import os

import numarray as num
import pyfits

from getL1Data import getL1Data
from GtApp import GtApp
from parfile_new import Parfile

_L1DataPath = '/nfs/farm/g/glast/u33/jchiang/ASP/testdata/downlinks'
_ft2File = '/nfs/farm/g/glast/u33/jchiang/ASP/testdata/eg_diffuse_scData_0000.fits'

_startTime = 0

debug = False

l1List = 'l1Files.txt'
countMapFile = 'countMap.fits'
errorMapFile = 'errorMap.fits'

energyBins = 3

pixelSize = 1.0
nRa = 90
nDec = 90

output_dir = os.environ['output_dir']
os.chdir(output_dir)

start_time = float(os.environ['start_time'])
stop_time = float(os.environ['stop_time'])

gtcntsmap = GtApp('gtcntsmap')

# get list of input files
ft1, ft2 = getL1Data(start_time, stop_time, l1DataPath=_L1DataPath,
                     ft2File=_ft2File, startTime=_startTime)
print "Using downlink files: ", ft1
ft2 = ft2[0]

# put list of input files in a text file to feed to gtcntsmap
l1fp = open(l1List, 'w')
for ft1File in ft1:
    print >> l1fp, ft1File
    pass
l1fp.close()

gtcntsmap['evfile'] = '@' + l1List
gtcntsmap['scfile'] = ft2
gtcntsmap['outfile'] = countMapFile

gtcntsmap['emin'] = 30.
gtcntsmap['emax'] = 2e5
gtcntsmap['nenergies'] = energyBins + 1

gtcntsmap['use_lb'] = 'y' # put center of map at galactic 
gtcntsmap['glon'] = 180.0  # anti
gtcntsmap['glat'] = 0.0    # center

gtcntsmap['nra'] = nRa
gtcntsmap['ndec'] = nDec
gtcntsmap['x_pixel_size'] = pixelSize
gtcntsmap['y_pixel_size'] = pixelSize

gtcntsmap['chatter']

# should probably write entire parfile in a setup TP,
# then only read in worker TPs
#parfile_basename = os.environ['PIPELINE_TASK'] + '.txt'
#pars = Parfile(parfile_basename)
pars = Parfile()
pars['ft1file'] = gtcntsmap['evfile']
pars['ft2file'] = ft2    # need to generalize this for multiple FT2 files
pars['start_time'] = start_time
pars['stop_time'] = stop_time
pars['count_map'] = countMapFile
pars['error_map'] = errorMapFile
pars['model_file'] = os.path.join(os.environ['PYASPROOT'], 'data', 'source_model.xml')
pars.write()

if debug:
    print gtcntsmap.command()
else:
    gtcntsmap.run()

# also make a map of errors
cmHDUs = pyfits.open(countMapFile)
counts = cmHDUs[0].data
errors = num.sqrt(counts) # maybe better to use Gehrels 1986 Apj 303:336
pyfits.PrimaryHDU(errors).writeto(errorMapFile)
