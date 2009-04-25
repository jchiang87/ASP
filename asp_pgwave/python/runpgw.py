import os,sys
from gtutil import *
from GtApp import GtApp
import pyfits
import numarray as num
from newpgw2fits import *
from runsrcid import *
from creaXimageGif import *
from FitsNTuple import FitsNTuple
from refinePositions import refinePositions
from dbmanager import *

"""gtselect = GtApp('gtselect')
gtbin = GtApp('gtbin')
gtexposure = GtApp('gtexposure')"""
pgw=GtApp('pgwave2D','pgwave')
debug=0
def getpgwConfig():
        err=0
        try:
                db=dbmanager()
                no=db.getPgwaveConfig()
        except cx_Oracle.DatabaseError, message:
                no=[1, ' ', 1, '3.0', '3', 10, 5, 10]
                err=1
                #raise cx_Oracle.DatabaseError,message
        if err==0:
                db.close()
        return no


def pgwave(filein,no):
	"""param='bgk_choise=n circ_square=s N_scale=1 scala=\"3.0\" otpix=\"10\" n_sigma=3 median_box=5 kappa=3 min_pix=3 border_size=4 fitsio_choice=n recursive_choice=n verbose_level=0'
	command=pgwaveprog +' '+filein+' '+param
	print command
	os.system(command)"""
        #pgw=GtApp('pgwave2D','pgwave')
        #fixed parameters
        pgw['bgk_choise'] = 'n'
        pgw['input_bgk_file']=''
        pgw['circ_square']= 's'
        pgw['N_iterations'] = 1
        pgw['SN_ratio'] = 0
#        pgw['n_sigma'] = 3
#        pgw['median_box'] = 5
        pgw['n_sigma'] = 7
        pgw['median_box'] = 9
        pgw['border_size'] = 4
        pgw['fitsio_choice'] = 'n'
        pgw['recursive_choice'] = 'n'
        pgw['verbose_level'] = 0
        #input counts Map
        pgw['input_file']=filein
        #parameters read from the db
        pgw['N_scale']=no[2]
        pgw['scala']=no[3]
        pgw['kappa']=no[4]
        pgw['otpix']=no[5]
        #run pgwave2D
        pgw.run(print_command=True)

def runpgw(infile):
	workdir=os.getcwd()
	header = pyfits.open(infile)['GTI'].header
    	ontime= header['ONTIME']
	print ontime
	iscale=2
    	if ontime>43000:
		iscale=4
	print iscale
	sizex=360*iscale
	sizey=180*iscale
	scale=1./iscale
	ra=180.
	dec=0.
	rad=180.
	#mapPar=[ra,dec,'CAR',sizex,sizey,scale,rad,'CEL']
	mapPar=[ra,dec,'CAR',sizex,sizey,scale,'CEL']
	inmap1=infile.replace('.fits','_map.fits')  
	#if os.path.exists(inmap1)==False:
	makeMap(infile,mapPar,inmap1)
	aitmap=infile.replace('.fits','_map_ait.fits')
	#mapParAit=[0.,0.,'AIT',720,360,0.5,rad,'GAL']
	mapParAit=[0.,0.,'AIT',720,360,0.5,'GAL']
	makeMap(infile,mapParAit,aitmap)
	#sys.exit()
	no=getpgwConfig()
        pgwave(inmap1,no)
	outf=inmap1.replace('.fits','.list')

if __name__ == "__main__":
        from parfile_parser import Parfile
        from syncDataViewer import syncDataViewer
        from renameOutFiles import renameOutFiles

	os.chdir(os.environ['OUTPUTDIR'])

        pars = Parfile('pgwave_pars.txt', fixed_keys=False)
        pars['ft1File'] = 'Filtered_evt.fits'
        pars['pgwave_list'] = 'Filtered_evt_map.list'
        pars.write()

	runpgw(pars['ft1File'])
