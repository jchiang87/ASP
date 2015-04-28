import numpy as num
from FitsNTuple import FitsNTuple
import pyfits

class PowerLaw(object):
    def __init__(self, index, norm=1):
        self.index, self.norm = index, norm
    def __call__(self, energy):
        return self.norm*energy**self.index
    def integral(self, emin, emax):
        if self.index == -1:
            return self.norm*num.log(emax/emin)
        return self.norm/(self.index+1)*(emax**(self.index+1) -
                                         emin**(self.index+1))

def pl_integral(x1, x2, y1, y2):
    indx = num.log(y2/y1)/num.log(x2/x1)
    pref = y1/(x1**indx)
#    if indx == -1:
#        return pref*num.log(x2/x1)
    return pref/(indx+1)*(x2**(indx+1) - x1**(indx+1))

energies = FitsNTuple('exposure_map.fits', 'ENERGIES').Energy

foo = pyfits.open('exposure_map.fits')

pl = PowerLaw(-2.1)

for i in range(len(energies)-1):
    y1 = foo[0].data[:][:][i]*pl(energies[i])
    y2 = foo[0].data[:][:][i+1]*pl(energies[i+1])
    if i == 0:
        sum = pl_integral(energies[i], energies[i+1], y1, y2)
    else:
        sum += pl_integral(energies[i], energies[i+1], y1, y2)

foo[0].data = sum/pl.integral(energies[0], energies[-1])
foo.writeto('exp_integrated.fits', clobber=True)
