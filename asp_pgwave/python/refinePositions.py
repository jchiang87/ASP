"""
@file refinePositions.py

@brief Run pointfit to refine the source positions from pgwave.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import shutil
from read_data import read_data
from pointfit import Background
from fitter import Fitter, photonmap, Source
import pyfits

class PgwaveData(list):
    def __init__(self, infile='Filtered_evt_map.list'):
        self.header = open(infile).readline()
        self.data = read_data(infile)
        for id, ra, dec, ksignif in zip(self.data[0], self.data[3], 
                                        self.data[4], self.data[7]):
            self.append(Source(`id`, ra, dec))
            self[-1].ksignif = ksignif
    def write(self, outfile):
        output = open(outfile, 'w')
        output.write(self.header)
        for irow, source in enumerate(self):
            output.write("%4i" % self.data[0][irow])
            output.write("%8.1f %8.1f" % (self.data[1][irow],self.data[2][irow]))
            output.write("%12.4f%12.4f" % (source.ra, source.dec))
            for icol in range(5, len(self.data)):
                output.write("%10s" % self.data[icol][irow])
            output.write("\n")
        output.close()

def refinePositions(pgwave_list='Filtered_evt_map.list',
                    ft1File='Filtered_evt.fits'):
    srclist = PgwaveData(pgwave_list)
    data = photonmap(ft1File, pixeloutput=None, eventtype=-1)
    
    ft1 = pyfits.open(ft1File)
    ontime = ft1['GTI'].header['ONTIME']

    # Crude estimate based on default exposure for Background class
    exposure = ontime*1e3 
    bg = Background('galdiffuse', exposure=exposure)

    output = open('updated_positions.txt', 'w')
    for source in srclist:
        fit = Fitter(source, data, background=bg(), verbose=0)
        output.write(("%5s" + "  %8.3f"*7 + "\n") % 
                     (source.name, source.ra, source.dec, fit.ra, 
                      fit.dec, fit.delta, fit.TS, source.ksignif))
        source.ra, source.dec = fit.ra, fit.dec
    output.close()
    #
    # Move original list out of the way.
    #
    shutil.copy(pgwave_list, pgwave_list.replace('.list', '_old.list'))
    #
    # Write the updated list in its place.
    #
    srclist.write(pgwave_list)

if __name__ == '__main__':
    refinePositions()
