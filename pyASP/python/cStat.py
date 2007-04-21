"""
@brief Calculate Cash's C-stat.

@author W. Focke <focke@slac.stanford.edu>
"""

import numarray as num

logNFactorialArray = []
def logNFactorial(counts):
    global logNFactorialArray
    maxN = num.maximum.reduce(counts.flat)
    if maxN > len(logNFactorialArray):
        en = num.arange(maxN+1)
        en[0] = 1
        logNFactorialArray = num.add.accumulate(num.log(en))
        pass
    return logNFactorialArray[counts]

def deltaC(counts, model):
    """Calculate contribution to C-stat for each pixel.
    Not done."""

    deltaC = 2.0 * (model - counts * num.log(model) + logNFactorial(counts))

    return deltaC


