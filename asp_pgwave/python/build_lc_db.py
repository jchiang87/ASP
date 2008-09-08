"""
@brief Fill a 'database table' (a cPickled dictionary) with light curves
for all of the HealPixels that have a source detected in them by pgwave.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import glob
import cPickle
import numpy as num
from FitsNTuple import FitsNTuple
from AspHealPix import Pixel, SkyDir, CountsArray, ExposureArray, Healpix
from generateMaps import CountsArrayFactory, ExposureArrayFactory
from read_data import read_data
from databaseAccess import *

class LightCurve(object):
    def __init__(self, ra, dec):
        self.ra, self.dec = ra, dec
        self.tmin = []
        self.tmax = []
        self.counts = []
        self.exposure = []
    def append(self, tmin, tmax, counts, exposure):
        self.tmin.append(tmin)
        self.tmax.append(tmax)
        self.counts.append(counts)
        self.exposure.append(exposure)

def get_tlims(ft1file):
    gti = FitsNTuple(ft1file, 'GTI')
    return min(gti.START), max(gti.STOP)

class PixelDbState(object):
    def __init__(self):
        self.validPixels = self._readValidPixels()
        self.filledPixels = self._findFilledPixels()
    def _readValidPixels(self):
        sql = "select * from SOURCEMONITORINGPOINTSOURCE"
        def cursorFunc(cursor):
            pixels = {}
            for item in cursor:
                if item[0].find('HP') == 0:
                    pixels[self._key(item[0])] = item[0], item[2], item[3]
            return pixels
        return apply(sql, cursorFunc)
    def _key(self, name):
        return int(name[2:7])
    def _findFilledPixels(self):
        sql = "select * from SOURCEMONITORINGDATA"
        def cursorFunc(cursor):
            filledPixels = {}
            for item in cursor:
                filledPixels[item[0]] = 1
            keys = filledPixels.keys()
            keys.sort()
            return keys
        return apply(sql, cursorFunc)
    def isValidPixel(self, name):
        return self._key(name) in self.validPixels
    def havePixel(self, name):
        return name in self.filledPixels

def insertData(sourcename, datatype, starttime, endtime, mean, rms,
               frequency='daily', isupperlimit=0, xmlfile='none'):
    sql = ("insert into SOURCEMONITORINGDATA (SOURCENAME, DATATYPE, "
           + "STARTTIME, ENDTIME, MEAN, RMS, FREQUENCY, ISUPPERLIMIT, XMLFILE)"
           + "values ('%s', '%s', %i, %i, %.5e, %.5e, '%s', %i, '%s')"
           % (sourcename, datatype, starttime, endtime, mean, rms, 
              frequency, isupperlimit, xmlfile))
    apply(sql)

def addPixelFluxes(hot_pixels, downlink, dbState, datatype='flux_100_300000'):
    """Add data points from the most recent downlink to the trending
    tables."""

    datapath = lambda x : os.path.join(downlink, x)
    tmin, tmax = get_tlims(datapath('FT1_merged.fits'))

    cmapfile = datapath('counts_%s.fits' % os.path.basename(downlink))
    emapfile = datapath('exposure_%s.fits' % os.path.basename(downlink))
    cmap = CountsArray(cmapfile)
    emap = ExposureArray(emapfile)

    missing_pixels = []
    for pix in hot_pixels:
        pixelName = dbState.validPixels[pix][0]
        if dbState.havePixel(pixelName):
            my_dir = SkyDir(hot_pixels[pix].ra(), hot_pixels[pix].dec())
            counts = cmap[my_dir]
            exposr = emap[my_dir]
            if exposr > 1:
                flux = counts/exposr
                error = num.sqrt(counts)/exposr
                insertData(pixelName, datatype, tmin, tmax, flux, error)
        else:
            missing_pixels.append(pix)
    return missing_pixels

def insertLightCurve(sourcename, datatype, lightCurve, frequency='daily',
                     isupperlimit=0, xmlfile='none'):
    connect_args = ("glastgen", "glast06", "GLASTP")
    my_connection = cx_Oracle.connect(*connect_args)
    cursor = my_connection.cursor()
    lc = lightCurve
    for tmin, tmax, counts, exposr in zip(lc.tmin, lc.tmax, 
                                          lc.counts, lc.exposure):
        if exposr > 1:
            mean = counts/exposr
            rms = num.sqrt(counts)/exposr
            sql = ("insert into SOURCEMONITORINGDATA (SOURCENAME, DATATYPE, "
                   + "STARTTIME, ENDTIME, MEAN, RMS, FREQUENCY, ISUPPERLIMIT, "
                   + "XMLFILE)"
                   + "values ('%s', '%s', %i, %i, %.5e, %.5e, '%s', %i, '%s')"
                   % (sourcename, datatype, tmin, tmax, mean, rms,
                      frequency, isupperlimit, xmlfile))
            cursor.execute(sql)
    cursor.close()
    my_connection.commit()
    my_connection.close()

def addLightCurve(pixel, downlinks, dbState, datatype='flux_100_300000'):
    """Add the flux estimates for a pixel for a list of downlinks."""
    sourcename = dbState.validPixels[pixel][0]
    ra, dec = dbState.validPixels[pixel][1], dbState.validPixels[pixel][2]
    lc = LightCurve(ra, dec)
    my_dir = SkyDir(ra, dec)
    for downlink in downlinks:
        datapath = lambda x : os.path.join(downlink, x)
        try:
            tmin, tmax = get_tlims(datapath('FT1_merged.fits'))

            cmapfile = datapath('counts_%s.fits' % os.path.basename(downlink))
            cmap = CountsArray(cmapfile)

            emapfile = datapath('exposure_%s.fits' % os.path.basename(downlink))
            emap = ExposureArray(emapfile)
            
            lc.append(tmin, tmax, cmap[my_dir], emap[my_dir])
        except IOError:
            pass
        pass
    insertLightCurve(sourcename, datatype, lc)

if __name__ == '__main__':
    pgwave_dir = os.path.dirname(os.environ['OUTPUTDIR'])
    os.chdir(pgwave_dir)
    
    downlinks = glob.glob(os.path.join(pgwave_dir, '0*'))
    downlinks.sort()

#    #
#    # kluge: hardwire FT2 file for Interleave55d
#    #
#    ft2file = '/nfs/farm/g/glast/u44/MC-tasks/Interleave55d-GR-v11r17/prune/FT2_55day_patch.fits'

    hp = Healpix(16, Healpix.NESTED, SkyDir.GALACTIC)
    #
    # Read in current pixel info.
    #
    try:
        lightCurves = cPickle.load(open('lc_data'))
    except IOError:
        lightCurves = {}
    hot_pixels = {}
    for key in lightCurves:
        hot_pixels[key] = Pixel(SkyDir(*hp.pix2coord(key)), hp)
        
    #
    # Add interesting pixels from current downlink.
    #
    datapath = lambda x : os.path.join(os.environ['OUTPUTDIR'], x)
    pgwave = read_data(datapath('Filtered_evt_map.list'))
    for ra, dec in zip(pgwave[3], pgwave[4]):
        pix = Pixel(SkyDir(ra, dec), hp)
        hot_pixels[pix.index()] = pix
        
    #
    # Rebuild light curves for all pixels:
    #
    lightCurves = {}
    for downlink in downlinks:
        datapath = lambda x : os.path.join(downlink, x)
        try:  # we can be fairly fault-tolerant here if there is a missing file
            tmin, tmax = get_tlims(datapath('FT1_merged.fits'))
        
            cmapfile = datapath('counts_%s.fits' % os.path.basename(downlink))
            if not os.path.isfile(cmapfile):
                break
            cmap = CountsArray(cmapfile)

            emapfile = datapath('exposure_%s.fits' %
                                os.path.basename(downlink))
            if not os.path.isfile(emapfile):
                break
            emap = ExposureArray(emapfile)

            for pix in hot_pixels:
                my_dir = SkyDir(hot_pixels[pix].ra(), hot_pixels[pix].dec())
                if not lightCurves.has_key(pix):
                    lightCurves[pix] = LightCurve(my_dir.ra(), my_dir.dec())
                lightCurves[pix].append(tmin, tmax, cmap[my_dir], emap[my_dir])
        except IOError:
            pass

    try:
        os.rename('lc_data', 'lc_data_save')
    except OSError:
        pass
    cPickle.dump(lightCurves, open('lc_data', 'w'), protocol=2)
    os.system('chmod 666 lc_data')

    #
    # Fill trending database with flux values
    #
    dbState = PixelDbState()

    #
    # First, handle pixels that already have historical light curves,
    # so just update using last downlink
    #
    try:
        missing_pixels = addPixelFluxes(hot_pixels, downlinks[-1], dbState)
        #
        # now add pixels that do not yet have historical light curves
        #
        for pixel in missing_pixels:
            print "adding light curve for pixel", pixel
            addLightCurve(pixel, downlinks, dbState)
    except:
        print "Available downlinks"
        print downlinks

