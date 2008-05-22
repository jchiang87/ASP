import readFT,angdist 
import os, glob,sys,math
import numpy as num

def getLC(dat,x1,y1,radius):
	nevt=len(dat[0])
	#print x1,y1,x2,y2
	#ngti=len(dat[4])
	r1=radius+2.
	r2=radius+4.
	res=radius*radius/(r2**2-r1**2)
	s=[]
	b=[]
	#dt=[]
	for i in range(0,nevt-1):
	  flag=0
	  if dat[1][i]>=100.:
		if angdist.angDistance(dat[2][i],dat[3][i],x1,y1)<radius:
			s.append((dat[0][i]-dat[0][0])/(3600.))
			flag=1
		if angdist.angDistance(dat[2][i],dat[3][i],x1,y1)>=r1 and angdist.angDistance(dat[2][i],dat[3][i],x1,y1)<=r2:
			flag=2
			b.append((dat[0][i]-dat[0][0])/(3600.))
	return s,b,res

def ave(a):
	if len(a)>1.:
		return sum(a)/len(a)
	else:
		return 0.

def stdev(a):
	mea=ave(a)
	if mea<=0.:
		return 0.
	som=0.
	for i in range(0,len(a)):
		som+=(a[i]-mea)*(a[i]-mea)
	h=som/(len(a)-1)
		
	return math.sqrt(h)

def chi2(a):
	mea=ave(a)
	if mea<=0.:
		return 0.
	som=0.
	for i in range(0,len(a)):
		som+=(a[i]-mea)*(a[i]-mea)/float(mea)
	return som/float(len(a))

def histo(tim,nbins):
	#fp=open(filen,"w")
	if(nbins>0):
				
		step=(tim[-1]-tim[0])/nbins
		h=[]
		tm=[]
		for j in range(0,nbins):
			k=0
			np=0.
			lo=tim[0]+j*step
			hi=lo+step
			mean=0.
			for t in tim:
				if(t>=lo and t<hi):
					#mean+=flu[k]
					np+=1.
				k+=1
			h.append(np)
			#tm.append(1.+lo)
			#fp.write("%6.2f\t%6.2e\n" % (lo+1.,mean/np))
	return h

def createLC(filin,obj,ra0,dec0,radius,nbins):
	
	evt=readFT.ReadFT1(filin)
	ene=evt.GetEnergy()
	time=evt.GetTime()
	ra=evt.GetRa()
	dec=evt.GetDec()
	tstart=evt.tstart
	tstop=evt.tstop
	#print tstart,len(time)
	dat=[time,ene,ra,dec,tstart,tstop]
	#print evt.GetTotalTime()
	#nbin=(time[len(time)-1]-time[0])/(24*3600.)
	#step=5.
	#st=step/2.
	
	t,b,res=getLC(dat,ra0,dec0,radius)
	if len(t)>1 and len(b)>1:
		co=num.array(histo(t,nbins))
		bg=num.array(histo(b,nbins))*res
		net=co-bg
	#print co,bg,net
		return chi2(net),sum(net),stdev(net)
	else:
		return 0.,0.,0.

if __name__=='__main__':

	createLC('nicola5.fits','ppp',128.,-45., 3.)
