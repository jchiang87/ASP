"""
@file refinePositions.py

@brief Run pointfit to refine the source positions from pgwave.
Filter out zero pointfit TS sources for abs(glat) < 5 deg.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import shutil
from read_data import read_data
import numpy as num
from pointfit import Background
from fitter import Fitter, photonmap, Source, SkyDir
import pyfits
import celgal
import databaseAccess as dbAccess
import pyfits
from FitsNTuple import FitsNTuple

def getIrfs(ft1file):
    ft1 = pyfits.open(ft1file)
    tmin, tmax = ft1[1].header['TSTART'], ft1[1].header['TSTOP']
    sql = ("select IRFS from SOURCEMONITORINGCONFIG where " +
           "STARTDATE<=%i and ENDDATE>=%i" % (tmin, tmax))
    def readIrfs(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, readIrfs)

converter = celgal.celgal()

def saveSource(source, glat_cutoff, TS_cutoff):
    ll, bb = converter.gal((source.ra, source.dec))
    if num.abs(bb) > glat_cutoff and source.TS <= TS_cutoff:
        print source.name, source.ra, source.dec
    if num.abs(bb) > glat_cutoff or source.TS > TS_cutoff:
        return True
    return False

class PgwaveData(list):
    def __init__(self, infile='Filtered_evt_map.list'):
        self.header = open(infile).readline()
        self.data = read_data(infile)
        for id, ra, dec, ksignif in zip(self.data[0], self.data[3], 
                                        self.data[4], self.data[7]):
            self.append(Source(`id`, ra, dec))
            self[-1].ksignif = ksignif
    def write(self, outfile, glat_cutoff=5, TS_cutoff=0):
        output = open(outfile, 'w')
	self.header=self.header.replace('SNR','TS ')
        output.write(self.header)
        for irow, source in enumerate(self):
            save_source = saveSource(source, glat_cutoff, TS_cutoff)
            ll, bb = converter.gal((source.ra, source.dec))
            print source.name, ll, bb, save_source
            if save_source:
                output.write("%4i" % self.data[0][irow])
                output.write("%8.1f %8.1f" % (self.data[1][irow],
                                              self.data[2][irow]))
                output.write("%12.4f%12.4f%12.4f%12.4f" % (source.ra, source.dec,self.data[5][irow],source.TS))
                for icol in range(7, len(self.data)):
                    output.write("%10s" % self.data[icol][irow])
                output.write("\n")
        output.close()

def refinePositions(pgwave_list='Filtered_evt_map.list',
                    ft1File='Filtered_evt.fits', glat_cutoff=5,
                    TS_cutoff=9, use_bg=True):
    irfs = getIrfs(ft1File)
     
    srclist = PgwaveData(pgwave_list)
    data = photonmap(ft1File, pixeloutput=None, eventtype=-1)
    
    events = FitsNTuple(ft1File)
    ft1 = pyfits.open(ft1File)
    ontime = ft1['GTI'].header['ONTIME']

    if use_bg:
        # Crude estimate based on default exposure for Background class
        exposure = ontime*1e3 
        bg = Background('galdiffuse', exposure=exposure)
    else:
        bg = lambda : None

    output = open('updated_positions.txt', 'w')
    for source in srclist:
        output.write(("%5s" + "  %8.3f"*2) % 
                     (source.name, source.ra, source.dec))
        fit = Fitter(source, data, background=bg(), verbose=0)
        source.ra, source.dec, source.TS = fit.ra, fit.dec, fit.TS
        if source.TS < TS_cutoff:
            ll, bb = converter.gal((source.ra, source.dec))
            if num.abs(bb) > glat_cutoff:
                dists = []
                for coord in zip(events.RA, events.DEC):
                    dists.append(celgal.dist(coord, (source.ra, source.dec)))
                dists = num.array(dists)
                indx = num.where(dists < 3)
                norm = sum(events.ENERGY[indx]**2)
                source.ra = sum(events.RA[indx]*events.ENERGY[indx]**2)/norm
                source.dec = sum(events.DEC[indx]*events.ENERGY[indx]**2)/norm
                source.sdir = SkyDir(source.ra, source.dec)
                print "calling Fitter with ", source.ra, source.dec
                fit = Fitter(source, data, background=bg(), verbose=0)
                print "fitted values: ", fit.ra, fit.dec
                source.ra, source.dec, source.TS = fit.ra, fit.dec, fit.TS
        output.write(("  %8.3f"*6 + "\n") % 
                     (source.ra, source.dec, fit.sigma, fit.delta, 
                      fit.TS, source.ksignif))
    output.close()
    #
    # Move original list out of the way.
    #
    shutil.copy(pgwave_list, pgwave_list.replace('.list', '_old.list'))
    #
    # Write the updated list in its place.
    #
    srclist.write(pgwave_list, glat_cutoff, TS_cutoff)
    rows = open(pgwave_list).readlines()
    return len(rows) - 1

if __name__ == '__main__':
    import os
    from parfile_parser import Parfile
    os.chdir(os.environ['OUTPUTDIR'])

    pars = Parfile('pgwave_pars.txt', fixed_keys=False)

    nsource = 0
    rows = open(pars['pgwave_list']).readlines()
    if len(rows) > 1:
        nsource = refinePositions(pars['pgwave_list'], pars['ft1File'])

    pars['nsource'] = nsource
    pars.write()

    
