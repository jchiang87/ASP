"""
@brief create light curves using aperture photometry method
"""
#
# $Header$
#
import gtutil
import aperPhotLC
import sys
import pyfits
import databaseAccess as dbAccess

def getIrfs(ft1file):
    ft1 = pyfits.open(ft1file)
    tmin, tmax = ft1[1].header['TSTART'], ft1[1].header['TSTOP']
    sql = ("select IRFS from SOURCEMONITORINGCONFIG where " +
           "STARTDATE<=%i and ENDDATE>=%i" % (tmin, tmax))
    def readIrfs(cursor):
        for entry in cursor:
            return entry[0]
    return dbAccess.apply(sql, readIrfs)

def createLC(lcpar,nbin,srcname,infile='Filtered_evt.fits',ft2file='FT2_merged.fits',irf=None):
        if irf is None:
#                irf = 'P6_V1_SOURCE'
#                irf = 'P8R2_SOURCE_V6'
                irf = 'P8R3_SOURCE_V2'
        else:
                irf = getIrfs(infile)
	outf='pgw_lc.dat'
	regfile='pgw_lc_variable.reg'
	mean=0.
	sig=0.
	chi2=0.
        V=0.
	res=aperPhotLC.getApPhotLC(infile,ft2file,irf,nbin,lcpar,srcname,outf)
	if len(res)<2:
		return 0,0,0,0
	if len(res[4]>nbin/2):
		mean,sig,chi2,findex,V=aperPhotLC.lcStat(res[4],res[5],res[8])
	f=open(outf,'a')
	print >>f,'Mean Flux:',mean
	print >>f,'stdev Flux:',sig
	print >>f,'Total Flux:',res[6]
	print >>f,'Total Flux error:',res[7]
	print >>f,'Reduced Chi^2:',chi2
	print >>f,'McLaughlin V index:',V
	f.close()
	f1=open(regfile,'a')
	#if chi2>1. and V>1.:
	print >>f1,('fk5;circle(%f,%f,%f)'%(lcpar[0],lcpar[1],lcpar[2]))
	print >>f1,('fk5;annulus(%f,%f,%f,%f)'%(lcpar[0],lcpar[1],lcpar[3],lcpar[4]))
	#outpl=srcname+'_lc.png'
	#aperPhotLC.plotLC(res[0],res[1],res[4],res[5],tit=srcname,outplot=outpl)
	f1.close()
	return res[6],res[7],chi2,V

if __name__=='__main__':

        nbin=6
        ra=128.
        dec=-45.
        emin=100.
        emax=2e5
        rsrc=3.
        r1bg=5.
        r2bg=7.
	tmin,tmax=gtutil.getFileTimeInfo('Filtered_evt.fits')
        lcpar=[ra,dec,rsrc,r1bg,r2bg,tmin,tmax,emin,emax,100.]
	mean,sig,chi2,V=createLC(lcpar,nbin,'undef')
	print mean,sig,chi2,V
