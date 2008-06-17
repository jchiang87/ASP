import gtutil
import aperPhotLC
import sys
def createLC(lcpar,nbin,srcname,infile='Filtered_evt.fits',ft2file='FT2_merged.fits',irf='P5_v13_0_source'):
	outf='pgw_lc.dat'
	regfile='pgw_lc_variable.reg'
	mean=0.
	sig=0.
	chi2=0.
	res=aperPhotLC.getApPhotLC(infile,ft2file,irf,nbin,lcpar,srcname,outf)
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
	if chi2>1. and V>1.:
		print >>f1,('fk5;circle(%f,%f,%f)'%(lcpar[0],lcpar[1],lcpar[2]))
		print >>f1,('fk5;annulus(%f,%f,%f,%f)'%(lcpar[0],lcpar[1],lcpar[3],lcpar[4]))
		outpl=srcname+'_lc.png'
		aperPhotLC.plotLC(res[0],res[1],res[4],res[5],outplot=outpl)
	f1.close()
	return res[6],res[7],chi2,V

if __name__=='__main__':

        nbin=6
        ra=63.1417
        dec=-18.8783
        emin=100
        emax=2e5
        rsrc=3.
        r1bg=5.
        r2bg=7.
	tmin,tmax=gtutil.getFileTimeInfo('Filtered_evt.fits')
        lcpar=[ra,dec,rsrc,r1bg,r2bg,tmin,tmax,emin,emax]
	mean,sig,chi2=createLC(lcpar,nbin)
	print mean,sig,chi2
