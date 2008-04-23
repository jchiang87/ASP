"""
@file makeAfterglowPlots.py

@brief Create spectrum and light curve plots for afterglow analysis.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os

# blech.  @todo rationalize use of OUTPUTDIR vs output_dir.  The
# following is needed by the makeRefinementPlots import.
os.environ['OUTPUTDIR'] = os.environ['output_dir']

os.environ['MPLCONFIGDIR'] = os.environ['OUTPUTDIR']

import numpy as num
import pylab
from FitsNTuple import FitsNTuple

from makeRefinementPlots import countsSpectra

def afterglow_lc(grbName, grb_id, lcfile, outfile=None):
    lc = FitsNTuple(lcfile)
    met = int(lc.TIME[0])
    tstep = (lc.TIME[1] - lc.TIME[0])
    times = lc.TIME - met
    fluxes, fluxerrs = [], []
    for counts, exposure in zip(lc.COUNTS, lc.EXPOSURE):
        if exposure > 0:
            fluxes.append(counts/exposure)
            fluxerrs.append(num.sqrt(counts)/exposure)
        else:
            fluxes.append(0)
            fluxerrs.append(0)
    pylab.plot(times-tstep/2., fluxes, 'k-', ls='steps')
    pylab.axis([times[0], times[-1], 0, max(fluxes + fluxerrs)*1.1])
    pylab.errorbar(times, fluxes, yerr=fluxerrs, fmt=None, ecolor='k')
    pylab.xlabel('MET - %i (s)' % met)
    pylab.ylabel('Flux (>100 MeV)')
    pylab.title('Light Curve')
    if outfile is None:
        outfile = 'lightCurve_afterglow_%i.png' % grb_id
    pylab.savefig(outfile)
    pylab.close()    

if __name__ == '__main__':
    import databaseAccess as dbAccess
    import pipeline

    os.chdir(os.environ['OUTPUTDIR'])
    grb_id = int(os.path.basename(os.getcwd()))

    pipeline.setVariable('GRB_ID', '%i' % grb_id)
    
    sql = "select GCN_NAME from GRB where GRB_ID=%i" % grb_id
    def getInfo(cursor):
        for entry in cursor:
            return entry[0]
    grbName = dbAccess.apply(sql, getInfo)

    countsSpectra(grb_id, grbName + '_afterglow_spec.fits',
                  outfile='countsSpectra_afterglow_%i.png' % grb_id)
    afterglow_lc(grbName, grb_id, grbName + '_afterglow_lc.fits')
