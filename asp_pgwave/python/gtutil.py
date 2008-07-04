import os
import pyfits
from GtApp import GtApp

gtselect = GtApp('gtselect')
gtbin = GtApp('gtbin')
gtexposure = GtApp('gtexposure')
fselect=GtApp('fselect')


def makeMap(infile,mapPar,outfil):
	gtbin.debug=False
	gtbin['algorithm']='CMAP'
	gtbin['evfile']=infile
	gtbin['outfile']=outfil
	gtbin['scfile']='NONE'
	gtbin['coordsys']=mapPar[6]
	gtbin['nxpix']=mapPar[3]
	gtbin['nypix']=mapPar[4]
	gtbin['proj']=mapPar[2]
	gtbin['xref']=mapPar[0]
	gtbin['yref']=mapPar[1]
	gtbin['binsz']=mapPar[5]
	gtbin.run()

def fsel(infile,cut,outfile):
	fselect['infile']=infile
	fselect['outfile']=outfile
	fselect['expr']=cut
	fselect['clobber']="yes"
	fselect.run()	

def select(infileft1,selPar,outfil):
        gtselect['infile'] = infileft1
        gtselect['outfile'] = outfil
        gtselect['tmin'] = int(selPar[3])
        gtselect['tmax'] = int(selPar[4])
        gtselect['ra'] =selPar[0]
        gtselect['dec'] =selPar[1]
        gtselect['rad'] = selPar[2]
        gtselect['emin'] = selPar[5]
        gtselect['emax'] = selPar[6]
#        gtselect['convtype'] = selPar[8]
#        gtselect['zmax']=selPar[7]
        gtselect.run()

def makeLC(ft1file,lcpar,outfile,ft2file='NONE'):
	gtbin['evfile']=ft1file
	gtbin['outfile']=outfile
	gtbin['algorithm']='LC'
	gtbin['scfile']=ft2file	
	gtbin['tbinalg']='LIN'
	gtbin['tstart']=lcpar[0]
	gtbin['tstop']=lcpar[1]
	gtbin['dtime']=lcpar[2]
	gtbin.run()

def lcExposure(lcfile,ft2file,irf):
	gtexposure['lcfile']=lcfile
	gtexposure['scfile']=ft2file
	gtexposure['rspfunc']=irf
	gtexposure['spectral_index'] = -2.1
	gtexposure['emin']=100.
	gtexposure.run()

def getFileTimeInfo(infile):
    ft1 = pyfits.open(infile)[1]
    return ft1.header["TSTART"], ft1.header["TSTOP"]


if __name__=='__main__':
	sizex=720
	sizey=360
	scale=0.5
	ra=180.
	dec=0.
	rad=180.
	#selpar=[ra,dec,rad,tmin,tmax,emin,emax,zmax,evclass]
	mapPar=[ra,dec,'CAR',sizex,sizey,scale,'CEL']
	makeMap('test_evt.fits',mapPar,'test_map.fits')
