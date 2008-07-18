import pyfits,commands,sys
import numpy as num
import os
from math import *
from readpgw import *
import newlc
import gtutil
from AspHealPix import CountsArray, ExposureArray, SkyDir
from creaXimageGif import *

def getFlux(ra,dec,counts):
	outdir=output_dir = os.environ['OUTPUTDIR']
	suff=os.path.basename(outdir)
	emapfile='exposure_'+suff+'.fits'
	#emapfile='exposure_00001.fits'
	emap = ExposureArray(emapfile)
	flux=num.zeros(len(ra),dtype=num.float)
	errflux=num.zeros(len(ra),dtype=num.float)
	for i in range(0,len(ra)):
		exposure_value=(emap[SkyDir(ra[i], dec[i])])
		if exposure_value>0 and counts[i]>0:
			flux[i]=counts[i]/exposure_value
			errflux[i]=num.sqrt(counts[i])/exposure_value
	return flux,errflux

def eqgal(ra,dec):

        conv=num.pi/180.000000000
        r=ra*conv
        d=dec*conv
        gal=num.array([[-0.054875539726, -0.873437108010, -0.483834985808],[ 0.494109453312e0, -0.444829589425e0,  0.746982251810e0],
        [ -0.867666135858, -0.198076386122,  0.455983795705]])
        v=num.array([ cos(d) * cos(r),cos(d) * sin(r),sin(d)])
        u=num.dot(gal,v)
        r2 = u[0]*u[0] + u[1]*u[1]
        l= 0.0
        b=-999
        if (r2  == 0.0):
              if (u[2] == 0.0):      
                return l,b      
              if u[2]>0.0:
                b=90.0 
              else: 
                b=-90.0
                return l,b
        b= atan( u[2] / sqrt(r2) )/conv
        l= atan2(u[1] , u[0])/conv
        if (l< 0.0): 
                l+= 360.0
        return l,b

def eq2gal(r,d):

	l=[]
	b=[]
	for i in range(0,len(r)):
		l0,b0=eqgal(r[i],d[i])
		l.append(l0)
		b.append(b0)
		#print l0,b0
	return num.array(l),num.array(b)

def pgw2fits(pgwfile,no,flag,nsource):
	debug=0
	pgwfits=pgwfile.replace('.list','_pgw_out.fits')
	filevt=pgwfile.replace('_map.list','.fits')
	name_pgw,ra_pgw,dec_pgw,posErr,signi_pgw=readpgw(pgwfile)
	l_pgw,b_pgw=eq2gal(ra_pgw,dec_pgw)
	#if debug==0:
	#	creaXimageGif('Filtered_evt_map_ait.fits',l_pgw,b_pgw)
	#posErr=[]
	count=[]
	chi2=[]
	fla=[]
	lines=open(pgwfile).readlines()
	tmppgw=open('tmplist.list','w')
	tmppgw.write(lines[0])
	print '---Variability check----'
	#filevt=os.path.join(os.environ['INPUTFT1DIR'],os.environ['INPUTFT1FILE'])
	chi=0.
	nbins=no[0] #5
	radius=3.0
        emin=100
        emax=2e5
        tmin,tmax=gtutil.getFileTimeInfo('Filtered_evt.fits')
	if (tmax-tmin)>40000:
		nbins=6
	if (tmax-tmin)>86400:
		nbins=7
        llcpar=[0.,0.,radius,5.,7.,tmin,tmax,100,2e5]
	flux=[]
	errflux=[]
	ra=[]
	dec=[]
	signi=[]
	srcname=[]
	l=[]
	b=[]
	pe=[]
	print "NAME            RA       DEC    SIGNIF  Flux  CHI2"
	
	for i in range(0,len(ra_pgw)):
		#print "NAME            RA       DEC    SIGNIF  Flux  CHI2"
		if flag==1: # and signi_pgw[i]>7.0:
			llcpar[0]=ra_pgw[i]
		        llcpar[1]=dec_pgw[i]
			fl,errfl,chi,V=newlc.createLC(llcpar,nbins,name_pgw[i])
			if fl==0:
			  continue
			tmppgw.write(lines[i+1])	
			l.append(l_pgw[i])
			b.append(b_pgw[i])
			pe.append(posErr[i])
			srcname.append(name_pgw[i])
			ra.append(ra_pgw[i])
			dec.append(dec_pgw[i])
			signi.append(signi_pgw[i])	
			flux.append(fl)
			errflux.append(errfl)
			if chi>=2. and V >1.:
				chi2.append(chi)
				fla.append(1)
				print name_pgw[i],'\t',ra_pgw[i],'\t',dec_pgw[i],'\t',signi_pgw[i],'\t',fl,'\t',chi
			else:
				fla.append(0)
				chi=0.
				chi2.append(0)
				print name_pgw[i],'\t',ra_pgw[i],'\t',dec_pgw[i],'\t',signi_pgw[i],'\t',fl,'\t',chi

		else:
			chi2.append(0)
			flux.append(0)
			errflux.append(0)
			fla.append(0)
			print name_pgw[i],'\t',ra_pgw[i],'\t',dec_pgw[i],'\t',signi_pgw[i],'\t',chi
	c1=pyfits.Column(name='NAME',format='10A', unit=' ',array=srcname)
	c2=pyfits.Column(name='RAJ2000',format='5F',unit='deg', array=num.array(ra))
	c3=pyfits.Column(name='DECJ2000',format='5F', unit='deg', array=num.array(dec))
	c4=pyfits.Column(name='Theta95', format='5F', unit='deg ',array=num.array(pe))
        c5=pyfits.Column(name='L', format='5F', unit='deg',array=num.array(l))        
	c6=pyfits.Column(name='B', format='5F', unit='deg',array=num.array(b))
	c7=pyfits.Column(name='Flux(E>100)', format='6F', unit='ph/cm^2s^-1',array=num.array(flux))
	c8=pyfits.Column(name='errFlux', format='6F', unit=' ',array=num.array(errflux))

	c9=pyfits.Column(name='CHI_2_VAR', format='5F', unit=' ',array=num.array(chi2))
	c10=pyfits.Column(name='FLARING_FLAG', format='1F', unit=' ',array=num.array(fla))
	c11=pyfits.Column(name='K_SIGN', format='1F', unit=' ',array=num.array(signi))

	x = pyfits.ColDefs([c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11])
	tbhdu=pyfits.new_table(x)
	tbhdu.writeto('temp.fits',clobber='yes')
	hd=(pyfits.open(filevt))[0].header   
     # add UCD in header
  	hdulist = pyfits.open('temp.fits')
  	head1 = hdulist[1].header
	head1.update('EXTNAME','PGWCAT',' ')
	head1.update('DATE-OBS',hd['DATE-OBS'],'')
	head1.update('DATE-END',hd['DATE-END'],'')
	head1.update('TBUCD2','POS_EQ_RA_MAIN','')
  	head1.update('TBUCD3','POS_EQ_DEC_MAIN','')
  	head1.update('TBUCD4','ERROR','')
	hdulist.writeto(pgwfits,clobber='yes')
	commands.getoutput('rm test.fits')
	#os.environ['PGWOUTPUTFITSLIST']=pgwfits
	if debug==0:                
		creaXimageGif('Filtered_evt_map_ait.fits',num.array(l),num.array(b))
	tmppgw.close()
	cmd='mv tmplist.list '+pgwfile
	commands.getoutput(cmd)
	cmd='mv pgw_lc_variable.reg Filtered_evt_map.reg'
	commands.getoutput(cmd)
	return pgwfits	
if __name__=="__main__":
	#os.environ['HOME'] = os.environ['output_dir']
	pgwfile=sys.argv[1]
	nrows=open(pgwfile).readlines()
	nsrc=len(nrows)-1
	pgw2fits(pgwfile,[5,10],1,nsrc)
