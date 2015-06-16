#
# $Header$
#
import numpy as num
from HealPix import Healpix, SkyDir, CountsArray, ExposureArray
import hippoplotter as plot

def spin(ra):
    if ra > 180:
        return ra - 360
    else:
        return ra

def plot_test(nside=4, intvl=0.05):
    from time import sleep
    import hippoplotter as plot
    nt = plot.newNTuple(([], [], []), ('RA', 'Dec', 'section'))
    disp = plot.Scatter(nt, 'RA', 'Dec', xrange=(-180, 180), yrange=(-90, 90))
    disp.setTransform('HammerAito')

    hp = Healpix(nside, Healpix.NESTED, SkyDir.EQUATORIAL)

    section = 0
    for pix in hp:
        nt.addRow((spin(pix.ra()), pix.dec(), section))
        if (pix.index()+1) % 2**nside == 0:
            sleep(intvl)
        if (pix.index()+1) % nside**2 == 0:
            section += 1
        if pix.index() == 25:
            ra_val = pix.ra()
            dec_val = pix.dec()

    print hp.coord2pix(ra_val, dec_val)
    print hp.pix2coord(25)
    print hp[25]().ra(), hp[25]().dec()

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
    def __call__(self, index, rotate=0, axis=None):
        if rotate and axis is None:
            axis = SkyDir(0, 0, self.coordsys)
        my_dir = SkyDir(self.hp[index]().ra(), self.hp[index]().dec())
        if rotate:
            my_dir = self._rotate(my_dir, axis, rotate)
        if self.coordsys == SkyDir.EQUATORIAL:
            return (spin(my_dir.ra()), my_dir.dec(),
                    self.hpArray[my_dir], self.section[index])
        else:
            return (spin(my_dir.l()), my_dir.b(),
                    self.hpArray[my_dir], self.section[index])
    def _rotate(self, indir, axis, angle):
        return SkyDir(indir().rotate(axis(), angle))
    def __getattr__(self, attrname):
        try:
            return getattr(self.hp, attrname)
        except AttributeError:
            return getattr(self.hpArray, attrname)
    def plot(self, section_cut=False):
        hp_nt = plot.newNTuple(([], [], [], []),
                               ('l', 'b', 'zvalue', 'section'))
        for i in range(self.npix()):
            hp_nt.addRow(self(i))
        disp = plot.XYZPlot(hp_nt, 'l', 'b', 'zvalue')
        disp.setTransform('HammerAito')
        if section_cut:
            sectionCut = plot.hippo.Cut(hp_nt, ('section',))
            sectionCut.addTarget(disp)
            plot.canvas.addDisplay(sectionCut)
            sectionCut.setCutRange(3.5, 4.5, 'x')
        return disp

if __name__ == '__main__':
    foo = HpArrayWrapper(CountsArray(Healpix(16, Healpix.NESTED,
                                             SkyDir.GALACTIC)))
                                             
    foo.binCounts('test_events_0000.fits')
    foo.plot()

    filename = 'foo.fits'
    foo.write(filename)

    bar = HpArrayWrapper(CountsArray(filename))
    bar.plot()
    
    exposure = HpArrayWrapper(ExposureArray(bar.hp))
    exposure.computeExposure('HANDOFF', 'expCube.fits')
    exposure.plot()
