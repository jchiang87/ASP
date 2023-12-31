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
import copy

from pointfit import photonmap
from asp_skymaps import DiffuseFunction, Background
from asp_pointlike import SkyDir, SourceList, Source, PointSourceLikelihood
#from skymaps import DiffuseFunction, Background
#from pointlike import SkyDir, SourceList, Source, PointSourceLikelihood

converter = celgal.celgal()

def saveSource(source, glat_cutoff, TS_cutoff):
    ll, bb = converter.gal((source.dir.ra(), source.dir.dec()))
    tts = source.TS()
    if num.abs(bb) > glat_cutoff and tts <= TS_cutoff:
        print source.name, source.dir.ra(), source.dir.dec(), tts
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
                print "saveSource == True for", source
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

def convert_for_pointfit(infile, outfile):
    ft1 = pyfits.open(infile)
    data = copy.deepcopy(ft1['EVENTS'].data)
    for i, item in enumerate(data.field('CONVERSION_TYPE')):
        data.field('EVENT_CLASS')[i] = item
    ft1['EVENTS'].data = data
    ft1.writeto(outfile, clobber=True)

def refinePositions(pgwave_list,
                    ft1File, glat_cutoff=5,
                    TS_cutoff=10, use_bg=True):

    print "working on", ft1File
    shutil.copy(ft1File, 'FT1_non_pointfit_saved.fits')
    convert_for_pointfit(ft1File, ft1File)
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
        diffusefilename = os.environ['GALPROP_MODEL']
	diffuse = DiffuseFunction(diffusefilename)
        bg = Background(diffuse, exposure)
	PointSourceLikelihood.set_diffuse(bg)
    	PointSourceLikelihood.set_energy_range(100,300000)
    else:
        bg = lambda : None
    output = open('updated_positions.txt', 'w')
    output.write("#Pgw_Ra pgw_Dec RA DEC Delta TS pgw_ksignif\n")
    for source in srclist:
	output.write( ("%5s  %8.3f%8.3f") % ((source.name),(source.dir.ra()),
                                             source.dir.dec()))
        fit = PointSourceLikelihood(data.map(), source.name, source.dir)
        source.dir, source.TS = fit.dir(), fit.TS
        sigma = fit.localize(2)
	source.sigma = sigma
	print source.name, source.dir.ra(), source.dir.dec(), sigma, source.TS()
        output.write(("  %8.3f"*5 + "\n") % (source.dir.ra(), source.dir.dec(),
                                             sigma, fit.TS(), source.ksignif))
    output.close()
    #
    # Move original list out of the way.
    #
    print "Move original list out of the way."
    shutil.copy(pgwave_list, pgwave_list.replace('.list', '_old.list'))
    #
    # Write the updated list in its place.
    #
    print "writing the updated list"
    srclist.write(pgwave_list, glat_cutoff, TS_cutoff)
    print "copying to a saved_source_list"
    shutil.copy(pgwave_list, 'saved_source_list')
    shutil.copy('FT1_non_pointfit_saved.fits', ft1File)

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
