import pyfits
import sys,pyASP

def d2dms(degree):
    "This function translates from degree to (degree , minute, second)"
    if degree < 0.0:
        neg = 1
    else:
        neg = 0

    degree = abs(degree)
    deg = int(degree)
    degree = degree - deg
    minute = int(degree * 60.0)
    degree = degree - minute / 60.0
    sec = degree * 3600
 
    if neg:
        if deg > 0:
            deg = -deg
        elif minute > 0:
            minute = -minute
        else:
            sec = -sec
    return deg, minute, sec
    
def d2dmstext(degree,sign=0):
	d,m,s=d2dms(degree)
	d1=d+int(m+int(s+0.5)/60)/60
	m1=m+int((s+0.5)/60)
	if m1>m:
		s1=0
	else:
		s1=s+0.5
	if sign==0:
		ss="%02d%02d%02d" % (int(d1),int(m1),int(s1))
	else:
		ss="%+03d%02d%02d" % (int(d1),int(m1),int(s1))
	return ss

def d2hmstext(degree):
	return d2dmstext(degree/15.)
	
def sphd2shptext(ra,dec):
	return d2dmstext(ra/15.)+d2dmstext(dec,1)

def tjd2jd(tjd):
        return (2440000.5+tjd)

def tjd2mjd(tjd):
        return (40000.+tjd)

def getSunPos(jdd):
	jd=pyASP.JulianDate(jdd)
	sun=pyASP.SolarSystem(pyASP.SolarSystem.SUN)
	dd=sun.direction(jd)
	return dd

def getMoonPos(jdd):
	jd=pyASP.JulianDate(jdd)
	moon=pyASP.SolarSystem(pyASP.SolarSystem.MOON)
	dd=moon.direction(jd)
	return dd
def getEventTimeInterval(infile):
	ft1=pyfits.open(infile)
	gti=ft1[2].data
	fthdr=ft1[1].header
	start=gti.field('START')[0]
	stop=gti.field('STOP')[-1]
	dt=stop-start
	dateobs=fthdr['DATE-OBS']
	gr=fthdr['DATE-OBS'].split('T')
	year=gr[0].split('-')
	ut=gr[1].split(':')
	utt=(float(ut[0])+float(ut[1])/60.+float(ut[0])/3600.)
	mstart=pyASP.JulianDate(int(year[0]),int(year[1]),int(year[2]),utt)
	mjdstart=tjd2jd(mstart.tjd())
	mjdstop=mjdstart+(stop-start)/86400.
	midjd=(mjdstart+mjdstop)/2.
	d={"tstart":start,"tstop":stop,"date":dateobs,"jdstart":mjdstart,"jdstop":mjdstop, "tdiff":dt,"midjd":midjd}
	return d

if __name__=='__main__':
	d=getEventTimeInterval(sys.argv[1])
	print d
	sunpos=getSunPos(d["midjd"])
	print sunpos.ra(), sunpos.dec()
	sunpos=getSunPos(d["jdstop"])
        print sunpos.ra(), sunpos.dec()
