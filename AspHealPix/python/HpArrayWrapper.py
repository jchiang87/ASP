"""
@file HpArrayWrapper.py
@brief Wrapper for HealpixArray objects providing plotting and
attribute access to underlying HealpixArray and Healpix objects.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import numpy as num
from HealPix import Healpix, SkyDir, HealpixArray, CountsArray, ExposureArray
import hippoplotter as plot

class HpArrayWrapper(object):
    def __init__(self, healpixArray):
        self.hpArray = healpixArray
        self.hp = healpixArray.healpix()
        self._set_sections()
        self.coordsys = self.hp.coordsys()
    def _set_sections(self):
        nside = self.hp.nside()
        self.section = []
        for i in range(self.hp.npix()/nside/nside):
            self.section.extend(list(i*num.ones(nside*nside)))
    def __getattr__(self, attrname):
        try:
            return getattr(self.hp, attrname)
        except AttributeError:
            return getattr(self.hpArray, attrname)
    def plot(self, section_cut=False):
        hp_nt = plot.newNTuple((self.hpArray.glon(), self.hpArray.glat(),
                                self.values(), self.section),
                                ('l', 'b', 'zvalue', 'section'))
        disp = plot.XYZPlot(hp_nt, 'l', 'b', 'zvalue')
        disp.setTransform('HammerAito')
        if section_cut:
            sectionCut = plot.hippo.Cut(hp_nt, ('section',))
            sectionCut.addTarget(disp)
            plot.canvas.addDisplay(sectionCut)
            sectionCut.setCutRange(3.5, 4.5, 'x')
        return disp
