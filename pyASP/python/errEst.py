"""
@brief Estimate errors using the trial points from the findSrc output
file, assuming the -log-Likelihood surface is azimuthally symmetric
about the minimum and can be fit by a paraboloid near the minimum.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import numarray as num
from read_data import read_data
from pyASP import SkyDir

def errEst(infile='findSrc.txt', makeplot=False):
    ra, dec, logLike, err = read_data(infile)

    minDir = SkyDir(ra[-1], dec[-1])
    indx = num.where(logLike < logLike[-1] + 2)

    ra = ra[indx]
    dec = dec[indx]
    logLike = logLike[indx]

    dist = num.array([SkyDir(*pair).difference(minDir)*180./num.pi
                      for pair in zip(ra, dec)])
    d2 = dist**2

    y = logLike - logLike[-1]
    AA = (len(d2)*sum(d2*y)-sum(y)*sum(d2))/(len(d2)*sum(d2**2)-(sum(d2))**2)

    if makeplot:
        import hippoplotter as plot
        from FunctionWrapper import FunctionWrapper
        nt = plot.newNTuple((ra, dec, dist, d2, logLike),
                            ('ra', 'dec', 'dist', 'd2', 'logLike'))
        plot.Scatter(nt, 'd2', 'logLike')
        f = FunctionWrapper(lambda x : AA*x + logLike[-1])
        plot.scatter(d2, f(d2), oplot=1, pointRep='Line')

    return 1./num.sqrt(2*AA)

if __name__ == '__main__':
    print errEst(makePlot=True)
