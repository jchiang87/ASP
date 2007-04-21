#!/usr/bin/env python

"""
@brief Find flaring sources by comparing countsmap with modelmap.

Currently incompatible with other steps because it ignores energy.

@author W. Focke <focke@slac.stanford.edu>
"""

import os

import numarray as num
import pyfits

from parfile_new import Parfile
import cStat

cThreshhold = 10.0 # utterly bogus value


output_dir = os.environ['output_dir']
os.chdir(output_dir)

pars = Parfile()
countMapFile = pars['count_map']
modelMapFile = pars['model_map']

## We can get the from the FITS files?
#raPars = eval(pars['ra_pars']) # should be a tuple of numbers ##security
#decPars = eval(pars['dec_pars']) # should be a tuple of numbers ##security

counts = pyfits.open(countMapFile)[0].data
model = pyfits.open(modelMapFile)[0].data

# likelyhood for each pixel
cBins = cStat.deltaC(counts, model)

hotEne, hotDec, hotRa = num.where((cBins > cThreshhold) & (counts > model))
hotVals = cBins[hotEne, hotDec, hotRa]

print len(hotVals)

# map from bin numbers to ra, dec
## need to write binCenters
## and
## write raPars, decPars to parfile during setup
##
## or can we call WCSlib?
##
#hotRa = binCenters(hotRa, raPars)
#hotDec = binCenters(hotDec, decPars)

# write out list of hotspots
## TBD
