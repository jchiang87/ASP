import os
#
# Need to set this so that pylab can write .matplotlib
#
os.environ['MPLCONFIGDIR'] = os.environ['OUTPUTDIR']
import matplotlib
matplotlib.use('Agg')

import sys,commands
import gtutil
import pyfits
import FitsNTuple
import pylab
import numpy as num
import statUtil
def getApPhotLC(infile,ft2file,irf,nbin,lcpar,srcname,outfile='lc.dat'):
	selpar=[]
	#tbin=(lcpar[6]-lcpar[5])/float(nbin)
	for i in range(0,3):
		selpar.append(lcpar[i])
	for i in range(5,len(lcpar)):                
		selpar.append(lcpar[i])
	#print selpar
	#sys.exit()
	factor=(lcpar[2]*lcpar[2]/(lcpar[4]*lcpar[4]-lcpar[3]*lcpar[3]))
	srcsel='vv.fits'
	gtutil.select(infile,selpar,srcsel)
	cut1="%f <= ENERGY && ENERGY <=%f && %i<= TIME && TIME <=%i && " %(lcpar[7],lcpar[8],int(lcpar[5]),int(lcpar[6]))
	cut2="angsep(RA,DEC,%f,%f) >= %f && angsep(RA,DEC,%f,%f) <=%f && gtifilter()" % (lcpar[0],lcpar[1],lcpar[3],lcpar[0],lcpar[1],lcpar[4])
	bgsel='vv_bg.fits'
	cut=cut1+cut2
	#if os.path.exists(bgsel):
	#	os.system('rm vv_bg.fits')
	gtutil.fsel(infile,cut,bgsel)
	nevtsr=(pyfits.open(srcsel)['EVENTS']).header['NAXIS2']
	bgevt=((pyfits.open(bgsel)['EVENTS']).header['NAXIS2'])*factor
	ontime=(pyfits.open(srcsel)['GTI']).header['ONTIME']
	netevt=(nevtsr-bgevt)
	if netevt<=0. or nevtsr<=0.:
		return [0]
	snr=netevt/num.sqrt(nevtsr)
	print 'S/N', snr, nevtsr, bgevt, netevt,netevt/ontime
	"""if snr<=2:
		return [0]"""
	dt=(lcpar[6]-lcpar[5])
	if dt<40000:
		nbin=3
	tbin=dt/float(nbin)
	#print "S/N ==", snr,"tbin=",tbin,"(s)" 
	parlc=[lcpar[5],lcpar[6],tbin]
	outlcsrc='vv_lc.fits'
	gtutil.makeLC(srcsel,parlc,outlcsrc)
	ncols=pyfits.open(outlcsrc)[1].header['NAXIS2']
	print ncols 
	try:
		gtutil.lcExposure(outlcsrc,ft2file,irf)
	except:
		print "Exposure calculation error"
		return [0]
	outlcbg='vv_bg_lc.fits'
        gtutil.makeLC(bgsel,parlc,outlcbg)
	ncol=pyfits.open(outlcsrc)[1].header['TFIELDS']
	if ncol<4:
		return [0]
	sr=FitsNTuple.FitsNTuple(outlcsrc)
	idx=num.where(sr.EXPOSURE>0.)
	id0=num.where(sr.EXPOSURE==0.)
	if len(id0)>1:
		print 'No Exposure in time bins:',sr.TIME[id0]-sr.TIMEDEL[id0]/2.,sr.TIME[id0]+sr.TIMEDEL[id0]/2.
	cn=sr.COUNTS[idx]
	esp=sr.EXPOSURE[idx]
	
	if len(esp)==1:
		return [0]
	srerr=num.sqrt(cn)
	bg=FitsNTuple.FitsNTuple(outlcbg)
	bgg=bg.COUNTS[idx]
	bgg=bgg*factor
	bgerr=num.sqrt(1+0.75*bgg)
	net=(cn-bgg)
	cnerr=num.sqrt(1+0.75*cn)
	neterr=num.sqrt(cn)
		
	flu=net/esp
	fluerr=neterr/esp
	flutot=sum(net)/sum(esp)
	flutoterr=num.sqrt(sum(net))/sum(esp)
	time=sr.TIME[idx]

	#print "Total exposure:",sum(esp)
	#print "S/N ==", snr,"tbin=",tbin,"(s)"
	f=open(outfile,'a')
	print >>f,'\n#Light curve for the object:',srcname
	print >>f,'#Coordinates (RA,DEC):',lcpar[0],',',lcpar[1]
	print >>f,'#MET Time interval (s): %i,%i'% (lcpar[5],lcpar[6])
	print >>f,'#Energy range (MeV): %i,%i'% (lcpar[7],lcpar[8])
	print >>f,'\n#Time(MET) Exposure Counts Err Flux Err'
	print >>f,'#T-%i'% lcpar[5]
	print '\n#Time(MET) Exposure Counts Err Flux Err'
        print '#T-%i'% lcpar[5]
	for t,es,c,e,fl,ferr in zip(time,esp,net,neterr,flu,fluerr):
		print ('%-11.4g '*6) % (t-lcpar[5],es,c,e,fl,ferr)
		print >>f,(('%-11.4g '*6) % (t-lcpar[5],es,c,e,fl,ferr))
	f.close()
	print 'Light curve data saved in: ',outfile
	commands.getoutput('rm vv.fits')
	commands.getoutput('rm vv_lc.fits')
	commands.getoutput('rm vv_bg.fits')
	commands.getoutput('rm vv_bg_lc.fits')
	cnfi=flu*(sum(esp)/(len(esp)))
	return [time,sr.TIMEDEL[idx],net,neterr,flu,fluerr,flutot,flutoterr,cnfi]

def lcStat(lc,lcerr,cn):
	sig2=lcerr*lcerr
	idx=num.where(sig2>0)
	dd=sig2[idx]
	if len(dd)<len(sig2):
		return 0.,0.,0.,0.,0.
	mean=sum(lc/sig2)/sum(1./sig2)
	sig=num.sqrt(1./(sum(1./sig2)))
	#print lc, (lc-mean)
	#chi2=sum(((lc-mean)*(lc-mean))/mean)
	#print cn
	chi2,prob=statUtil.chisquare(cn)
	chVag,McVag=statUtil.mcvaug(lc,lcerr,mean)
	fluct_ind=100.*sig/mean
	print 'mean = ',mean
	print 'stdev = ',sig
	print 'chi2 = ',chi2, 'dof = ',len(lc)-1, 'prob = ',prob
	print 'chi2McVag = ',chVag, 'dof = ',len(lc)-1, 'V = ',McVag
	print 'fluct_index(100*stdev/mean)=',fluct_ind
	return mean,sig,chi2/(len(lc)-1),fluct_ind,McVag

def plotLC(x,xerr,y,yerr,tit='Light curve',outplot='lc.png'):
	fig_width_pt = 550.0  # Get this from LaTeX using \showthe\columnwidth
	inches_per_pt = 1.0/72.27               # Convert pt to inch
	golden_mean = (pylab.sqrt(5)-1.0)/2.0         # Aesthetic ratio
	fig_width = fig_width_pt*inches_per_pt  # width in inches
	fig_height = fig_width*golden_mean      # height in inches
	fig_size =  [fig_width,fig_height]
	params = {'backend': 'eps',
          'axes.labelsize': 10,
	  'text.fontsize': 10,       
	  'xtick.labelsize': 10,
	  'ytick.labelsize': 10,
	  'text.usetex': True,
	  'figure.figsize': fig_size}
	pylab.rcParams.update(params)
	idx=num.where(y>0.)
	xx=x[idx]
	yy=y[idx]
	t=xx-xx[0]
	f=yy*1e6
	xer=xerr[idx]/2.
	t=t+xer
	yer=yerr[idx]*1e6
	pylab.figure(2)
	pylab.clf()
	#pylab.errorbar(t,f,xerr=xer,yerr=yer,fmt='bo',ecolor='black', ms=4,mfc='black',mec='black')
	pylab.errorbar(t,f,xerr=xer,yerr=yer,linewidth=0.4,fmt='bo',ecolor='black', ms=3,mfc='black',mec='black',antialiased='False', capsize=0.001)

	pylab.xlabel('MET (T-%i)[s]'%int(x[0]))
	#pylab.ylabel('F(E$>$100~MeV)~[10$^{-6}$~cm$^{-2}$~s$^{-1}$]')
	#pylab.xlabel(r"$\rm{MET}\  \rm{[s]}$",fontsize=13)
        pylab.ylabel(r"$\rm{Flux\ (E\ } > 100\ \rm{MeV)} \ \ \ \  [\times 10^{-6}\ \rm{ph}\ \  \rm{cm}^{-2}\ \rm{s}^{-1}]$",fontsize=12)

	tit=tit.replace('_',' ')
	pylab.title(tit)
	pylab.savefig(outplot)
	pylab.close('all')
	print 'Light curve plot saved in: ',outplot

if __name__=='__main__':
	infile='Filtered_evt.fits'
	ft2file='FT2_merged.fits'
#	irf='P6_V1_SOURCE'
	irf='P8R2_SOURCE_V6'
	#selpar=[ra,dec,rad,tmin,tmax,emin,emax,zmax,evclass]
	tmin,tstop=gtutil.getFileTimeInfo(infile)
	tmax=tmin+86400
	nbin=10
	zmax=100.
	evclass=-1
	ra=128.0
	dec=-45.0
	emin=100
	emax=1e5
	rsrc=3.
	r1bg=5.
	r2bg=7.
	lcpar=[ra,dec,rsrc,r1bg,r2bg,tmin,tmax,emin,emax,zmax,evclass]
	res=getApPhotLC(infile,ft2file,irf,nbin,lcpar,'Vela')
	lcStat(res[4],res[5],res[8])
	outplot='lc.png'
	plotLC(res[0],res[1],res[4],res[5],'Vela',outplot)
