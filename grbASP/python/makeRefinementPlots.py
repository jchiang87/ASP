"""
@file makeRefinementPlots.py
@brief Create the standard plots for the prompt GRB analysis.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
#
# Need to set this so that pylab can write .matplotlib
#
os.environ['MPLCONFIGDIR'] = os.environ['OUTPUTDIR']

import numpy as num
import pylab
import pyfits
from FitsNTuple import FitsNTuple
import pyASP
from SkyCone import makeCone
from read_data import read_data

def getAxisRange(header):
    naxis1 = header['naxis1']
    crpix1 = header['crpix1']
    crval1 = header['crval1']
    cdelt1 = header['cdelt1']
    xx = (num.arange(naxis1, dtype=num.float) - crpix1 + 1)*cdelt1 + crval1
    naxis2 = header['naxis2']
    crpix2 = header['crpix2']
    crval2 = header['crval2']
    cdelt2 = header['cdelt2']
    yy = (num.arange(naxis2, dtype=num.float) - crpix2 + 1)*cdelt2 + crval2
    return (xx[0], xx[-1], yy[0], yy[-1])

class CoordSys(object):
    def __init__(self, fitsfile):
        self.proj = pyASP.SkyProj(fitsfile)
        x0, x1, y0, y1 = self._getAxisRange(pyfits.open(fitsfile)[0].header)
        self.lonRange = x0, x1
        self.latRange = y0, y1
    def meridian(self, longitude, npts=50):
        dlat = (self.latRange[1] - self.latRange[0])/(npts - 1)
        lats = num.arange(self.latRange[0], self.latRange[1], dlat)
        x, y = [], []
        for latitude in lats:
            xx, yy = self.proj.sph2pix(longitude, latitude)
            x.append(xx)
            y.append(yy)
        return num.array(x), num.array(y)
    def circle_of_latitude(self, latitude, npts=50):
        dlon = (self.lonRange[1] - self.lonRange[0])/(npts - 1)
        lons = num.arange(self.lonRange[0], self.lonRange[1], dlon)
        x, y = [], []
        for longitude in lons:
            xx, yy = self.proj.sph2pix(longitude, latitude)
            x.append(xx)
            y.append(yy)
        return num.array(x), num.array(y)
    def _getAxisRange(self, header):
        nxpix = header['NAXIS1']
        nypix = header['NAXIS2']
        x, y = self.proj.pix2sph(0, 0)
        xmin = xmax = x
        ymin = ymax = y
        for i in range(nxpix):
            x, y = self.proj.pix2sph(i, 0)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
            x, y = self.proj.pix2sph(i, nypix + 1)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
        for j in range(nypix):
            x, y = self.proj.pix2sph(0, j)
            xmin = min(xmin, x)
            xmax = max(xmax, x)
            x, y = self.proj.pix2sph(nxpix + 1, j)
            xmin = min(xmin, x)
            xmax = max(xmax, x)
        return xmin, xmax, ymin, ymax
    def oplotCoords(self, lons, lats, format="%i"):
        xtics = []
        xticnames = []
        for i in lons:
            x, y = self.meridian(i)
            yabs = num.abs(y)
            indx = num.where(yabs == min(yabs))
            xtics.append(x[indx[0][0]])
            xticnames.append(format % i)
            pylab.plot(x, y, 'b:')
        pylab.xticks(xtics, xticnames)

        ytics = []
        yticnames = []
        for i in lats:
            x, y = self.circle_of_latitude(i)
            xabs = num.abs(x)
            indx = num.where(xabs == min(xabs))
            ytics.append(y[indx[0][0]])
            yticnames.append(format % i)
            pylab.plot(x, y, 'b:')
        pylab.yticks(ytics, yticnames)

def plotCircle(ra, dec, radius, color='r', proj=None):
    ras, decs = makeCone(ra, dec, radius)
    if proj is not None:
        xx, yy = [], []
        for coords in zip(ras, decs):
            x, y = proj.sph2pix(*coords)
            xx.append(x)
            yy.append(y)
        x, y = proj.sph2pix(ra, dec)
    else:
        x, y = ra, dec
        xx, yy = ras, decs
    pylab.plot([x], [y], '+', markersize=10, color=color)
    pylab.plot(xx, yy, '-', color=color)

def countsMap(grb_id, cmapfile, pos, init_pos, outfile=None):
    cmap = pyfits.open(cmapfile)
    axisRange = (1, cmap[0].header['NAXIS1'], 1, cmap[0].header['NAXIS2'])
    image = cmap[0].data.tolist()
    image.reverse()
    image = num.array(image)
    pylab.imshow(image, interpolation='nearest', 
                 cmap=pylab.cm.spectral_r, extent=axisRange, aspect='equal')
    pylab.colorbar(ticks=range(min(image.flat), max(image.flat)+2))

    coordSys = CoordSys(cmapfile)

    delta = 5.
    xmin = int(coordSys.lonRange[0]/delta)*delta
    xmax = int(coordSys.lonRange[1]/delta + 1)*delta
    ymin = int(coordSys.latRange[0]/delta)*delta
    ymax = int(coordSys.latRange[1]/delta + 1)*delta
    coordSys.oplotCoords(num.arange(xmin, xmax, delta), 
                         num.arange(ymin, ymax, delta))

    plotCircle(pos[0], pos[1], pos[2], proj=coordSys.proj)
    plotCircle(init_pos[0], init_pos[1], init_pos[2], color='w',
               proj=coordSys.proj)
    pylab.axis(axisRange)
    pylab.xlabel('RA (deg)')
    pylab.ylabel('Dec (deg)')
    pylab.title('Counts Map')
    if outfile is None:
        outfile = 'countsMap_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

def oplot_errors(x, y, yerr):
    for xx, yy, err in zip(x, y, yerr):
        if err == yy == 1:
            err = 0.999 # workaround for plotting bug in pylab for ylog plots
        pylab.plot([xx, xx], [yy-err, yy+err], 'k-')
        
def countsSpectra(grb_id, spectrumfile, outfile=None):
    counts = FitsNTuple(spectrumfile)
    ebounds = FitsNTuple(spectrumfile, 'EBOUNDS')
    energies = num.sqrt(ebounds.E_MIN*ebounds.E_MAX)

    axUpper = pylab.axes((0.1, 0.3, 0.8, 0.6))
    axUpper.loglog(energies, counts.ObsCounts, 'kD', markersize=3)
    oplot_errors(energies, counts.ObsCounts, num.sqrt(counts.ObsCounts))

    xrange = [min(energies)/2., max(energies)*2]

    yrange = [min(counts.ObsCounts - num.sqrt(counts.ObsCounts))/2, 
              max(counts.ObsCounts + num.sqrt(counts.ObsCounts))*2]
    if yrange[0] == 0:
        yrange[0] = 0.5

    modelSum = num.zeros(len(counts.ObsCounts))
    for item in counts.names:
        if item != 'ObsCounts':
            modelSum += counts.__dict__[item]
            pylab.plot(energies, counts.__dict__[item], 'k--')
    pylab.plot(energies, modelSum, 'k-')
    pylab.axis((xrange[0], xrange[1], yrange[0], yrange[1]))
    pylab.ylabel('counts / bin')
    pylab.title('Counts Spectra')

    residuals = (counts.ObsCounts - modelSum)/modelSum
    residual_errors = num.sqrt(counts.ObsCounts)/modelSum

    axLower = pylab.axes((0.1, 0.1, 0.8, 0.2))
    axLower.semilogx(energies, residuals, 'kD', markersize=3)
    oplot_errors(energies, residuals, residual_errors)

    pylab.plot([xrange[0]/10, xrange[1]*10], [0, 0], 'k--')
    pylab.axis((xrange[0], xrange[1], min(residuals - residual_errors)*2, 
                max(residuals + residual_errors)*1.1))
                
    pylab.xlabel('Energy (MeV)')
    pylab.ylabel('(counts - model) / model', fontsize=8)

    if outfile is None:
        outfile = 'countsSpectra_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

def createHist(xvals, xmin, xmax, nx=50):
    xstep = (xmax - xmin)/nx
    xx = num.arange(xmin, xmax, xstep)
    bins = num.zeros(nx)
    for val in xvals:
        indx = int((val - xmin)/xstep)
        try:
            bins[indx] += 1
        except IndexError:
            if val == xmax:
                bins[-1] += 1
    return xx, bins

def getTimeKeywords(fitsfile):
    foo = pyfits.open(fitsfile)
    return foo[1].header['TSTART'], foo[1].header['TSTOP'], foo

def lightCurve(grb_id, tstart, ft1file, outfile=None, bb_lc_file=None):
    tmin, tmax, ft1_pyfits = getTimeKeywords(ft1file)
    if ft1_pyfits['EVENTS'].size() != 0:
        ft1 = FitsNTuple(ft1file)
        tvals = ft1.TIME - int(tstart)
    else:
        tvals = []
    xx, yy = createHist(tvals, tmin - tstart, tmax - tstart)
    pylab.plot(xx, yy, 'k-', ls='steps')
    axisRange = [xx[0], xx[-1], 0, max(yy)*1.1]
    pylab.axis(axisRange)
    pylab.xlabel('MET - %i (s)' % int(tstart))
    pylab.ylabel('entries / bin')
    pylab.title('Light Curve')
    if bb_lc_file is not None:
        x, y = read_data(bb_lc_file)
        x -= int(tstart)
        pylab.plot(x, y, 'k--')
        pylab.axis(axisRange)
    if outfile is None:
        outfile = 'lightCurve_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

def tsMap(grb_id, fitsfile, ra, dec, outfile=None):
    ts = pyfits.open(fitsfile)
    axisRange = (1, ts[0].header['NAXIS1'], 1, ts[0].header['NAXIS2'])
    levels = max(ts[0].data.flat) - num.array((2.31, 4.61, 9.21))
    image = ts[0].data.tolist()
    image = num.array(image)
    contourSet = pylab.contour(image, levels, interpolation='nearest', 
                               extent=axisRange)
    #pylab.clabel(contourSet)

    coordSys = CoordSys(fitsfile)

    scaleFactor = float(10**(-int(num.log10(ts[0].header['CDELT1']))))

    deltax = max(int((coordSys.latRange[1] - coordSys.latRange[0])
                     /3.*scaleFactor), 1)/scaleFactor

    xmin = int(coordSys.lonRange[0]*scaleFactor)/scaleFactor
    xmax = int(coordSys.lonRange[1]*scaleFactor)/scaleFactor
    xrange = num.arange(xmin, xmax, deltax)

    deltay = max(int((coordSys.latRange[1] - coordSys.latRange[0])
                     /5.*scaleFactor), 1)/scaleFactor
    ymin = int(coordSys.latRange[0]*scaleFactor)/scaleFactor
    ymax = int(coordSys.latRange[1]*scaleFactor)/scaleFactor
    print scaleFactor
    print coordSys.latRange
    print ymin, ymax, deltay
    yrange = num.arange(ymin, ymax, deltay)

    coordSys.oplotCoords(xrange, yrange, format="%.2f")

    x, y = coordSys.proj.sph2pix(ra, dec)
    pylab.plot([x], [y], 'k+', ms=10)

    pylab.axis(axisRange)
    pylab.xlabel('RA (deg)')
    pylab.ylabel('Dec (deg)')
    pylab.title('Error Contours')
    if outfile is None:
        outfile = 'errorContours_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()
    return coordSys

if __name__ == '__main__':
    import glob
    from parfile_parser import Parfile
    from GtApp import GtApp
    import databaseAccess as dbAccess
    from refinePosition import likelyUL

    os.chdir(os.environ['OUTPUTDIR'])

    grb_id = int(os.environ['GRB_ID'])

    sql = ("select GCN_NAME, INITIAL_LAT_RA, INITIAL_LAT_DEC, " + 
           "INITIAL_ERROR_RADIUS from GRB where GRB_ID=%i and GCAT_FLAG=0" 
           % grb_id)
    def getInfo(cursor):
        for entry in cursor:
            return entry[0], float(entry[1]), float(entry[2]), float(entry[3])
    grbName, init_ra, init_dec, init_err = dbAccess.apply(sql, getInfo)
    
    pars = Parfile(grbName + '_pars.txt')

    #
    # Re-extract the FT1 data using the best-fit position and Bayesian
    # Block start and stop times.
    #
    ra, dec = pars['ra'], pars['dec']
    error = pars['loc_err']
    rad = 10
    tstart = pars['tstart']
    tstop = pars['tstop']
    duration = tstop - tstart

    if duration < 200:
        tmin = tstart - 10
        tmax = tstop + 10
    else:
        tmin = tstart
        tmax = tstop

    ft1file = grbName + '_for_plots.fits'
    gtselect = GtApp('gtselect')
    gtselect.run(infile='FT1_merged.fits', outfile=ft1file,
                 ra=ra, dec=dec, rad=rad*1.5, tmin=tmin, tmax=tmax,
                 emin=30, emax=3e5, zmax=100)
    lightCurve(grb_id, tstart, ft1file, bb_lc_file=grbName + '_BB_lc.dat')

    #
    # Use the FT1 file extracted for the time interval and best fit position
    #
    ft1file = grbName + '_LAT_3.fits'
    binsz = 0.5
    nxpix = int(2*rad/binsz)
    nypix = int(2*rad/binsz)

    cmapfile = 'cmap.fits'

    gtbin = GtApp('gtbin')
    gtbin.run(evfile=ft1file, scfile='FT2_merged.fits', outfile=cmapfile,
              algorithm='CMAP', nxpix=nxpix, nypix=nypix, binsz=binsz, 
              coordsys='CEL', xref=ra, yref=dec, proj='STG')

    countsMap(grb_id, cmapfile, (ra, dec, error), (init_ra, init_dec, init_err))
    countsSpectra(grb_id, grbName + '_grb_spec.fits')
    if not likelyUL(grb_id):
        tsMap(grb_id, grbName + '_tsmap.fits', ra, dec)
