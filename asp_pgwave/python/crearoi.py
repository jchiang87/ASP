"""
@brief For a list of point sources, generate a set of ROIs with a
given radius that covers them for Likelihood analysis.

@author Gino Tosti
"""
#
# $Header$
# 

import string, os, math,sys
import numpy

from read_data import read_data

DEG_RAD=math.pi/180.

def angDistance(ra1,dec1,ra2,dec2):
	ra1 = ra1*DEG_RAD;
	dec1 = dec1 * DEG_RAD;
	ra2 = ra2*DEG_RAD;
	dec2 = dec2 * DEG_RAD;
	x1 = math.cos(ra1)*math.cos(dec1);
	y1 = math.sin(ra1)*math.cos(dec1);
	z1 = math.sin(dec1);
	x2 = math.cos(ra2)*math.cos(dec2);
	y2 = math.sin(ra2)*math.cos(dec2);
	z2 = math.sin(dec2);
	costheta =(x1*x2+y1*y2+z1*z2)
	#print "cost=",costheta
	if(costheta>=1.):
		return 0
	return math.acos(costheta)/DEG_RAD
	
def initroi(pg_ra,pg_dec,dist):
	#tot=len(dc_ra)
	tot=len(pg_ra)
	idd=range(1,tot+1)
	fla=numpy.zeros(tot)
	roi_ra=[]
	roi_dec=[]
	rad=[]
	k=0
	for i in range(0,tot):
		r=pg_ra[i]
		d=pg_dec[i]
			
			#print idd[i],r,d
		if fla[i]==0.:
			k=k+1
			for j in range(0,tot):
				r1=pg_ra[j]
				d1=pg_dec[j]
				a=angDistance(r,d,r1,d1)
				if(a<=(dist-5) and a>=0.):
					fla[j]=k
					
					#print "   ",k,idd[j],r1,d1,a
				#print (("%3d   %6.2f    %6.2f  20  30 # %s")% (k,r1,d1,pg_nome[j]))
				#sn[j],'\t',signi[j],'\t',a 
		roi_ra.append(r)
		roi_dec.append(d)
		rad.append(dist)
	#print "non associate"
	for j in range(0,tot):
		if fla[j]==0:
			print pg_ra[j],pg_dec[j],fla[j]

	return roi_ra,roi_dec,rad

def makeroi(roi_ra,roi_dec,pg_ra,pg_dec,dist):
	
	k=0
	tot=len(pg_ra)
	tot1=len(roi_dec) 
	r_ra=[]
	r_dec=[]
	rad=[]
	fla=numpy.zeros(tot)
	for i in range(0,tot1):
		r=roi_ra[i]
		d=roi_dec[i]
		#print i,r,d
		k=0
		meanra=0
		meandec=0
		suma=0
		for j in range(0,tot):
			r1=pg_ra[j]
			d1=pg_dec[j]
			a=angDistance(r,d,r1,d1)
			if(a<=dist[i]-5 and a>0. and fla[j]==0.):
				fla[j]=1.
				meanra+=r1
				meandec+=d1
				suma+=1.
				k=k+1
				
				#print (("%3d   %6.2f    %6.2f  20  30 # %s")% (k,r1,d1,pg_nome[j]))
				#sn[j],'\t',signi[j],'\t',a 
		if suma>0.:
			r_ra.append(meanra/suma)
			r_dec.append(meandec/suma)
			rad.append(dist[i])
	return r_ra,r_dec,rad
	
def mergeroi(roi_ra,roi_dec,dist):
	
	k=0
	tot1=len(roi_dec) 
	r_ra=[]
	r_dec=[]
	fla=numpy.zeros(tot1)
	rad=[]
	for i in range(0,tot1):
		r=roi_ra[i]
		d=roi_dec[i]
		#print i,r,d
		
		k=0
		meanra=0
		meandec=0
		suma=0.
		dista=[]
		if fla[i]==0.:
			for j in range(0,tot1):
				r1=roi_ra[j]
				d1=roi_dec[j]
				a=angDistance(r,d,r1,d1)
				se=dist[i]
				if(a<=dist[i]/2 and a>0. and fla[j]==0.):
					fla[j]=1.
					meanra+=r1
					meandec+=d1
					suma+=1
		if suma>0.:
			r_ra.append(meanra/suma)
			r_dec.append(meandec/suma)
			#print max(dista)
			rad.append(dist[i])
		else:
			r_ra.append(roi_ra[i])
			r_dec.append(roi_dec[i])
			rad.append(dist[i])
	

	return r_ra,r_dec,rad

def getinside(r,d,pg_ra,pg_dec,dist,rad):
	k=1;
	flag=numpy.zeros(len(pg_ra))
	for j in range(0,len(r)):
	   #print "ROI:",j, "CENTER:",r[j],d[j]
	   for i in range(0,len(pg_ra)):
		r1=pg_ra[i]
		d1=pg_dec[i]
		a=angDistance(r[j],d[j],r1,d1)
		if(a<=(dist[j]) and flag[i]==0.):
			flag[i]=k
			#print "SOURCE",i, "ang:",a
	   k=k+1

		  	
	
	#if k<len(pg_ra) or len(r)>maxroi:
	kk=0
	for i in range(0,len(pg_ra)):
		if flag[i]==0.:
			r.append(pg_ra[i])
			d.append(pg_dec[i])
			dist.append(rad)
			#print "flaggo:",i
			kk=kk+1
	reg=[]
	for i in range(0,len(pg_ra)):
	    roi=[]
	    for j in range(0,len(r)):
		  a=angDistance(r[j],d[j],pg_ra[i],pg_dec[i])
		  if(a<=(dist[j])):
		  	roi.append(j+1)
	    reg.append(roi)
	return kk,reg
			
def printRoi(outfile,ra_fin,dec_fin,rad_fin,source):
	f=open(outfile,"w")
	print >>f,"# ID   RA    Dec   ROI_radius  SR_radius"
	for j in range(0,len(ra_fin)):
		print >>f,(("%3d   %6.2f    %6.2f  %6.2f  %6.2f #")% (j+1,ra_fin[j],dec_fin[j],rad_fin[j],rad_fin[j]+10.)),source[j]
		
#def crearoi(infile,dist):
#	#pg_nome,pg_ra,pg_dec,sn,counts=readpgw_roi(infile)
#	data=read_data(infile)
#	pg_nome=data[0]
#	pg_ra=data[3]
#	pg_dec=data[4]
def crearoi(pg_nome, pg_ra, pg_dec, dist, outfile):
	tot=len(pg_ra)
	#maxroi=len(pg_ra)/5
	idd=range(1,tot+1)
	fla=numpy.zeros(tot)
	k=0
	num=0
	r_ra,r_dec,rad=initroi(pg_ra,pg_dec,dist)
	while(True):
		roi_ra,roi_dec,rad1=makeroi(r_ra,r_dec,pg_ra,pg_dec,rad)
		r2_ra,r2_dec,rad=mergeroi(roi_ra,roi_dec,rad1)
		nins,reg=getinside(r2_ra,r2_dec,pg_ra,pg_dec,rad,dist)
		#print nins,tot
		if nins==0 or k>=10:
			break
		k=k+1
		r_ra=r2_ra
		r_dec=r2_dec
	source=[]
	idx1=numpy.zeros(len(pg_ra))
	for j in range(0,len(r2_ra)):
	   #print "ROI:",j+1,"XC=",r2_ra[j],"YC=",r2_dec[j]
	   kk=0
	   inreg=[]
	   for i in range(0,len(pg_ra)):
		r1=r2_ra[j]
		d1=r2_dec[j]
		b=angDistance(pg_ra[i],pg_dec[i],r1,d1)
		if(b<=rad[j] and idx1[i]==0):
			idx1[i]=1
			inreg.append(pg_nome[i])
			kk=kk+1
	   source.append(inreg)
	   #print "#sources in roi: ", kk,inreg	
	ra_fin=[]
	dec_fin=[]
	rad_fin=[]
	sour_fin=[]
	for j in range(0,len(r2_ra)):
		if len(source[j])>0:
			ra_fin.append(r2_ra[j])
			dec_fin.append(r2_dec[j])
			rad_fin.append(rad[j])
			sour_fin.append(source[j])
	
	printRoi(outfile,ra_fin,dec_fin,rad_fin,sour_fin)

if __name__ == '__main__':
	if len(sys.argv)<3:
		print "usage: python crearoi.py pgwaveListFile radius [outfile]"
		sys.exit()

	infile=sys.argv[1]
	radius=float(sys.argv[2])
        try:
                outfile = sys.argv[3]
        except:
                outfile = 'rois.txt'

        data = read_data(infile)
        id, ra, dec = data[0], data[3], data[4]

	crearoi(id, ra, dec ,radius, outfile)
