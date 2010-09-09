"""
@brief Insert entries into TIMEINTERVALS table based on nMetStart,
nMetStop of the most recent data delivery dataset that was processed
by L1Proc.

@author J. Chiang 
"""
#
# $Header$
#
import os

from intervalAccess import insertNewIntervals

nMetStart = int(float(os.environ['nMetStart']))
nMetStop = int(float(os.environ['nMetStop']))

if os.environ['PIPELINESERVER'] == 'DEV':
    omit_prior = True
else:
    omit_prior = False

insertNewIntervals(nMetStart, nMetStop, omit_prior_intervals=omit_prior)
