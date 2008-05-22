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

insertNewIntervals(nMetStart, nMetStop)
