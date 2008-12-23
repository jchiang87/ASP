#!/usr/bin/env python
"""
@file refinePositions.py

@brief Run pointfit to refine the source positions from pgwave.
Filter out zero pointfit TS sources for abs(glat) < 5 deg.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import shutil,os
from read_data import read_data
import pyfits
from FitsNTuple import FitsNTuple
import numpy as num
import celgal

from pointfit import photonmap
from pointlike import DiffuseFunction
from pointlike import SkyDir,SourceList, Source, PointSourceLikelihood, Background

converter = celgal.celgal()

def saveSource(source, glat_cutoff, TS_cutoff):
    ll, bb = converter.gal((source.dir.ra(), source.dir.dec()))
    tts = source.TS()
    if num.abs(bb) > glat_cutoff and tts <= TS_cutoff:
        print source.name, source.dir.ra(), source.dir.dec()
#    if num.abs(bb) > glat_cutoff or tts > TS_cutoff:
    if tts > TS_cutoff:
        return True
    return False

class PgwaveData(list):
    def __init__(self, infile='Filtered_evt_map.list'):
        self.header = open(infile).readline()
        self.data = read_data(infile)
        for id, ra, dec, ksignif in zip(self.data[0], self.data[3], 
                                        self.data[4], self.data[7]):

            s=Source()
	    s.name=str(id)
	    s.dir=SkyDir(ra,dec)
	    s.TS=ksignif
            self.append(s)
            self[-1].sigma = 0.0
            self[-1].ksignif = ksignif
    def write(self, outfile, glat_cutoff=5, TS_cutoff=0):
        output = open(outfile, 'w')
	hea=self.header.replace('SNR','PF_TS')
	hea=hea.replace('POS_','PF__')
        output.write(hea)
        for irow, source in enumerate(self):
            if saveSource(source, glat_cutoff, TS_cutoff):
                output.write("%4i" % self.data[0][irow])
                output.write("%8.1f %8.1f" % (self.data[1][irow],
                                              self.data[2][irow]))
                output.write("%12.4f%12.4f%12.4f%12.4f" % 
                             (source.dir.ra(), source.dir.dec(),
                              source.sigma,source.TS()))
                for icol in range(7, len(self.data)):
                    output.write("%10s" % self.data[icol][irow])
                output.write("\n")
        output.close()

def refinePositions(pgwave_list,
                    ft1File, glat_cutoff=5,
                    TS_cutoff=10, use_bg=True):

    srclist = PgwaveData(pgwave_list)
    data = photonmap(ft1File, pixeloutput=None, eventtype=-1)
    #data.info()

    events = FitsNTuple(ft1File)
    ft1 = pyfits.open(ft1File)
    ontime = ft1['GTI'].header['ONTIME']
    #print ontime
    if use_bg:
        # Crude estimate based on default exposure for Background class
        exposure = ontime*1e3 
#        diffusefilename = os.path.join(os.environ['EXTFILESSYS'],
#                                       'galdiffuse', 'GP_gamma.fits')
        diffusefilename = os.environ['GALPROP_MODEL']
	diffuse = DiffuseFunction(diffusefilename)
        bg = Background(diffuse, exposure)
	PointSourceLikelihood.set_diffuse(bg)
    	PointSourceLikelihood.set_energy_range(100,300000)
    else:
        bg = lambda : None
    output = open('updated_positions.txt', 'w')
#    k = 1
    output.write("#Pgw_Ra pgw_Dec RA DEC Delta TS pgw_ksignif\n")
    for source in srclist:
	output.write( ("%5s  %8.3f%8.3f") % ((source.name),(source.dir.ra()),
                                             source.dir.dec()))
        fit = PointSourceLikelihood(data.map(), source.name, source.dir)
        source.dir, source.TS = fit.dir(), fit.TS
	sigma = fit.localize(2)
	source.sigma = sigma
	print source.name, source.dir.ra(), source.dir.dec(), sigma, source.TS()
#        if source.TS() < TS_cutoff:
#            ll, bb = converter.gal((source.dir.ra(), source.dir.dec()))
#            if num.abs(bb) > glat_cutoff:
#                dists = []
#                for coord in zip(events.RA, events.DEC):
#                    dists.append(celgal.dist(coord, (source.dir.ra(), 
#                                                     source.dir.dec())))
#                dists = num.array(dists)
#                indx = num.where(dists < 3)
#                norm = sum(events.ENERGY[indx]**2)
#                ra1 = sum(events.RA[indx]*events.ENERGY[indx]**2)/norm
#                dec1 = sum(events.DEC[indx]*events.ENERGY[indx]**2)/norm
#                source.dir = SkyDir(ra1, dec1)
#                print "calling Fitter with ", source.dir.ra(), source.dir.dec()
#                fit = PointSourceLikelihood(data.map(), source.name, source.dir)
#                print "calling fit.localize"
#                sigma = fit.localize(2)
#                print "fitted values: ", fit.dir().ra(), fit.dir().dec()
#                source.dir, source.TS = fit.dir(), fit.TS
#	#print k,source.dir.ra(), source.dir.dec() #fit.dir().ra(), fit.dir().dec(), fit.TS()
#	#k=k+1
        output.write(("  %8.3f"*5 + "\n") % (source.dir.ra(), source.dir.dec(),sigma, fit.TS(), source.ksignif))
    output.close()
    #
    # Move original list out of the way.
    #
    shutil.copy(pgwave_list, pgwave_list.replace('.list', '_old.list'))
    #
    # Write the updated list in its place.
    #
    srclist.write(pgwave_list, glat_cutoff, TS_cutoff)

if __name__ == '__main__':
#    import sys
#    refinePositions(sys.argv[1],sys.argv[2],sys.argv[3])
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
