import os,sys
from GtApp import GtApp
import pyfits
import numarray as num
from pgw2fits import *
from runsrcid import *
from creaXimageGif import *
from FitsNTuple import FitsNTuple
#Sc2Ft2File=os.environ['INPUTFT2FILE']
#tSc2Data ='nicola5.fits'

gtselect = GtApp('gtselect')
gtbin = GtApp('gtbin')
gtexposure = GtApp('gtexposure')

pgwaveprog=os.path.join(os.environ['PGWAVEROOT'], os.environ['BINDIR'])+'/pgwave2D.exe'
#pgwaveprog='pgwave'

#def select(infileft1,mapPar,outfil):
#        gtselect['infile'] = infileft1
#        gtselect['outfile'] = outfil
#        #gtselect['tmin'] = 0
#        #gtselect['tmax'] = 0
#        #
#        # no time selection is desired, so need to pass tstart and tstop from
#        # input file here in order to get correct TSTART and TSTOP header
#        # keywords
#        #
#        gti = FitsNTuple(infileft1, 'GTI')
#        gtselect['tmin'] = min(gti.START)
#        gtselect['tmax'] = max(gti.STOP)
#        gtselect['ra'] =mapPar[0]
#        gtselect['dec'] =mapPar[1]
#        gtselect['rad'] = mapPar[6]
#        gtselect['emin'] = 100
#        gtselect['emax'] = 2e5
#        gtselect['eventClass'] = -1
#        gtselect['zmax']=105
#        gtselect.run()



def makeMap(infile,mapPar,outfil):
	gtbin.debug=False
	gtbin['algorithm']='CMAP'
	gtbin['evfile']=infile
	gtbin['outfile']=outfil
	gtbin['scfile']='NONE'
	"""gtbin['numxpix']=mapPar[3]
	gtbin['numypix']=mapPar[4]
	gtbin['proj']=mapPar[2]
	gtbin['xref']=mapPar[0]
	gtbin['yref']=mapPar[1]"""
	gtbin['coordsys']=mapPar[7]
	gtbin['nxpix']=mapPar[3]
	gtbin['nypix']=mapPar[4]
	gtbin['proj']=mapPar[2]
	gtbin['xref']=mapPar[0]
	gtbin['yref']=mapPar[1]
	gtbin['binsz']=mapPar[5]
	gtbin.run()

def makeLC(infile,lcPar,outfil):	
	gtbin['algorithm']='LC'
	gtbin['evfile']=infile
	gtbin['outfile']=outfil
	gtbin['scfile']=Sc2Ft2File
	gtbin['timebinalg']='LIN'
	gtbin['tstart']=lcPar[0]
	gtbin['tstop']=lcPar[1]
	gtbin['deltatime']=lcPar[2]
	gtbin.run()

def calcExposure(infile):	
	gtexposure['lcfile']=infile
	gtexposure['scfile']=Sc2Ft2File
	gtexposure['rspfunc']='Pass5_v0_source'
	gtexposure['spectral_index']=-2.1
	gtexposure.run()

def createMap(infil,mapPar,outf):
	makeMap(infil,mapPar,outf)

def pgwave(filein):
	param='bgk_choise=n circ_square=s N_scale=1 scala=\"3.0\" otpix=\"10\" n_sigma=3 median_box=5 kappa=3 min_pix=3 border_size=4 fitsio_choice=n recursive_choice=n verbose_level=0'
	command=pgwaveprog +' '+filein+' '+param
	print command
	os.system(command)


def runpgw(infile):
	workdir=os.getcwd()
	print 'Running PGWave in dir: ',workdir
#	tmp=infile
#	cmd='fcopy \"'+infile+'[EVENTS][CTBCLASSLEVEL>1]\"'+' Filtered.fits'
#        # fcopy has no clobber option, so we remove by hand.
#        try:
#                os.remove('Filtered.fits')
#        except OSError:
#                pass
#	os.system(cmd) 
	sizex=720
	sizey=360
	scale=0.5
	ra=180.
	dec=0.
	rad=180.
	#infile='Filtered.fits'
	mapPar=[ra,dec,'CAR',sizex,sizey,scale,rad,'CEL']
	#outfil='Filtered_evt.fits'
        # move this selection to getPgwInputData
#	select(infile,mapPar,outfil)
	inmap1=infile.replace('.fits','_map.fits')  #os.path.join(workdir,((os.environ['INPUTFT1FILE']).split('.')[0]+'_map.fits'))
	if os.path.exists(inmap1)==False:
		createMap(infile,mapPar,inmap1)
	aitmap=infile.replace('.fits','_map_ait.fits')
	mapParAit=[0.,0.,'AIT',sizex,sizey,scale,rad,'GAL']
	createMap(infile,mapParAit,aitmap)
	#creaXimageGif(aitmap)
        pgwave(inmap1)
	outf=inmap1.replace('.fits','.list')
	outfits=pgw2fits(outf,1)
	runsrcid(outfits,.01)
	print 'PGWave FITS output file:',outfits 
	#outf=os.path.abspath(pgwfile)
#	os.environ['PGWOUTPUTLIST']=pgwfile

if __name__=="__main__":
        from syncDataViewer import syncDataViewer
        from renameOutFiles import renameOutFiles

	os.chdir(os.environ['OUTPUTDIR'])

	runpgw('Filtered_evt.fits')

        syncDataViewer()
        renameOutFiles()

	os.system('chmod 777 *')
