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

def getAxisRange(header):
    naxis1 = header['naxis1']
    crpix1 = header['crpix1']
    crval1 = header['crval1']
    cdelt1 = header['cdelt1']
    xx = (num.arange(naxis1, dtype=num.float) - crpix1)*cdelt1 + crval1
    naxis2 = header['naxis2']
    crpix2 = header['crpix2']
    crval2 = header['crval2']
    cdelt2 = header['cdelt2']
    yy = (num.arange(naxis2, dtype=num.float) - crpix2)*cdelt2 + crval2
    return (xx[0], xx[-1], yy[0], yy[-1])

def plotCircle(ra, dec, radius, color='r'):
    dphi = 2*num.pi/20
    phi = num.arange(0, 2*num.pi + dphi, dphi)
    xx = radius*num.cos(phi) + ra
    yy = radius*num.sin(phi) + dec
    pylab.plot([ra], [dec], color+'+', markersize=10)
    pylab.plot(xx, yy, color+'-')

def countsMap(grbName, grb_id, cmapfile, pos, init_pos, outfile=None):
    cmap = pyfits.open(cmapfile)
    axisRange = getAxisRange(cmap[0].header)
    pylab.imshow(cmap[0].data, interpolation='nearest', 
                 cmap=pylab.cm.spectral_r, extent=axisRange)
    pylab.colorbar()

    plotCircle(pos[0], pos[1], pos[2])
    plotCircle(init_pos[0], init_pos[1], init_pos[2], color='k')
    pylab.axis(axisRange)
    pylab.xlabel('RA (deg)')
    pylab.ylabel('Dec (deg)')
    pylab.title('Counts Map')
    #pylab.show()
    if outfile is None:
        outfile = 'countsMap_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

def oplot_errors(x, y, yerr):
    for xx, yy, err in zip(x, y, yerr):
        pylab.plot([xx, xx], [yy-err, yy+err], 'k-')
        
def countsSpectra(grbName, grb_id, spectrumfile, outfile=None):
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

    #pylab.show()
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

def lightCurve(grbName, grb_id, ft1file, outfile=None):
    ft1 = FitsNTuple(ft1file)
    tvals = ft1.TIME - grb_id
    xx, yy = createHist(tvals, min(tvals), max(tvals))
    pylab.plot(xx, yy, 'k-', ls='steps')
    pylab.axis([xx[0], xx[-1], 0, max(yy)*1.1])
    pylab.xlabel('MET - %i (s)' % grb_id)
    pylab.ylabel('entries / bin')
    pylab.title('Light Curve')
    #pylab.show()
    if outfile is None:
        outfile = 'lightCurve_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

def tsMap(grbName, grb_id, fitsfile, ra, dec, outfile=None):
    ts = pyfits.open(fitsfile)
    axisRange = getAxisRange(ts[0].header)
    levels = max(ts[0].data.flat) - num.array((2.31, 4.61, 9.21))
    pylab.contour(ts[0].data, levels, interpolation='nearest',
                  extent=axisRange)
    pylab.plot([ra], [dec], 'k+', ms=10)
    pylab.xlabel('RA (deg)')
    pylab.ylabel('Dec (deg)')
    pylab.title('Error Contours')
    #pylab.show()
    if outfile is None:
        outfile = 'errorContours_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()

if __name__ == '__main__':
    import glob
    from parfile_parser import Parfile
    from GtApp import GtApp
    import databaseAccess as dbAccess

    os.chdir(os.environ['OUTPUTDIR'])

    grb_id = int(os.environ['GRB_ID'])

    sql = ("select GCN_NAME, INITIAL_LAT_RA, INITIAL_LAT_DEC, " + 
           "INITIAL_ERROR_RADIUS from GRB where GRB_ID=%i" % grb_id)
    def getInfo(cursor):
        for entry in cursor:
            return entry[0], float(entry[1]), float(entry[2]), float(entry[3])
    grbName, init_ra, init_dec, init_err = dbAccess.apply(sql, getInfo)
    
    pars = Parfile(grbName + '_pars.txt')

    ft1file = grbName + '_LAT_2.fits'
    ft1 = FitsNTuple(ft1file)

    ra, dec = pars['ra'], pars['dec']
    error = pars['loc_err']

    rad = 10
    binsz = 0.5
    nxpix = int(2*rad/binsz)
    nypix = int(2*rad/binsz)

    cmapfile = 'cmap.fits'

    gtbin = GtApp('gtbin')
    gtbin.run(evfile=ft1file, scfile='FT2_merged.fits', outfile=cmapfile,
              algorithm='CMAP', nxpix=nxpix, nypix=nypix, binsz=binsz, 
              coordsys='CEL', xref=ra, yref=dec, proj='STG')

    countsMap(grbName, grb_id, cmapfile, (ra, dec, error), 
              (init_ra, init_dec, init_err))
    lightCurve(grbName, grb_id, ft1file)
    countsSpectra(grbName, grb_id, grbName + '_grb_spec.fits')
    tsMap(grbName, grb_id, grbName + '_tsmap.fits', ra, dec)
