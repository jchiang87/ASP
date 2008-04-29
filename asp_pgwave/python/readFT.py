import sys,pyfits #pylab
import math
import numpy as num

def rad(a):
	return num.pi/180.*a

def deg(a):
	return 180./num.pi*a

class ReadFT1:
	def __init__(self,ft1file):
		self.ft1=pyfits.open(ft1file)
		self.evtstbl=self.ft1['EVENTS'].data
		self.evthead=self.ft1['EVENTS'].header
		self.gtitbl=self.ft1['GTI'].data
		self.tstart=self.evthead['TSTART']
		self.tstop=self.evthead['TSTOP']
		self.gtihead=self.ft1['GTI'].header
	def GetNevt(self):
		return self.evthead['NAXIS2']
	def GetNgti(self):
		return self.gtihead['NAXIS2']
	def GetRa(self):
		ra=self.evtstbl.field('RA')
		return ra
	def GetDec(self):
		dec=self.evtstbl.field('DEC')
		return dec
	def GetTime(self):
		ti=ra=self.evtstbl.field('TIME')
		return ti
	def GetEnergy(self):
		energy=self.evtstbl.field('ENERGY')
		return energy
	def GetEvtId(self):
		evtid=self.evtstbl.field('EVENT_ID')
		return evtid
	def GetRunId(self):
		runid=self.evtstbl.field('RUN_ID')
		return runid
	def GetEvtClass(self):
		classid=self.evtstbl.field('EVENT_CLASS')
		return classid
	def GetEvtClass(self):
		theta=self.evtstbl.field('THETA')
		return theta
	def GetL(self):
		gl=self.evtstbl.field('L')
		return gl
	def GetB(self):
		gb=self.evtstbl.field('B')
		return gb
	def GetTotalTime(self):
		total=(self.tstop-self.tstart)/3600.
		return self.tstart,self.tstop,total
	def CloseFT1(self):
		self.ft1.close()

class ReadFT2:
	def __init__(self,scFile):
		self.sc=pyfits.open(scFile)
		self.sctbl=sc['SC_DATA'].data
		self.start=self.sctbl.field('START')
		self.stop=self.sctbl.field('STOP')
		self.raz=self.sctbl.field('RA_SCZ')
		self.decz=self.sctbl.field('DEC_SCZ')
		self.insaa=self.sctbl.field('IN_SAA')
		self.livetime=self.sctbl.field('LIVETIME')
		self.sc.close()
		self.ndata=self.raz.size()
	def GetTstart(self):
		return self.start[0]
	def GetTstop(self):
		return self.stop[self.ndata]

def FT1EnergyCut(evtstbl,emin,emax):
		mask=num.and_(evtstbl.field('ENERGY')>=emin,evtstbl.field('ENERGY')<=emax)
		newtab= evtstbl[mask]
		return newtab
def FT1PhaseCut(evtstbl,emin,emax):
		mask=num.and_(evtstbl.field('PULSE_PHASE')>=emin,evtstbl.field('PULSE_PHASE')<=emax)
		newtab= evtstbl[mask]
		return newtab
def FT1ThetaCut(evtstbl,emin,emax):
		mask=num.and_(evtstbl.field('THETA')>=emin,evtstbl.field('THETA')<=emax)
		newtab= evtstbl[mask]
		return newtab


def angDistance(ra1,dec1,ra2,dec2):

	x1 = num.cos(ra1)*num.cos(dec1);
	y1 = num.sin(ra1)*num.cos(dec1);
	z1 = num.sin(dec1);
	x2 = num.cos(ra2)*num.cos(dec2);
	y2 = num.sin(ra2)*num.cos(dec2);
	z2 = num.sin(dec2);
	costheta =(x1*x2+y1*y2+z1*z2)
	return costheta

def Deviation(onpulse,ra,dec):
		ra2=rad(onpulse.field('RA'))
		dec2=rad(onpulse.field('DEC'))
		aa=angDistance(rad(ra),rad(dec),ra2,dec2)
		an=deg(num.arccos(aa))	
		return an
