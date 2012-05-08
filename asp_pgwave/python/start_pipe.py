import os

rootdir=os.getcwd()

os.environ['GTSRCID_CATALOG']='/Users/ginotosti/glast/Oktobertest/testpipe/catdir'
os.environ['FLAOUTDIR']=rootdir
#os.environ['OUTPUTDIR']='/Users/ginotosti/glast/Oktobertest'
os.environ['INPUTFT1FILE']='prime4h.fits'
os.environ['INPUTFT2FILE']='/Users/ginotosti/glast/Oktobertest/FT2_orbit18.fits'

from runPipe import *

downlink='down1'
try:
	os.mkdir(downlink)
except OSError:       
	pass

from runPipe import *

#os.system('chmod 777 %s ' % downlink)
out_dir = os.path.abspath(downlink)
os.environ['OUTPUTDIR']=os.path.abspath(downlink)
runPipe(output_dir=out_dir)
os.chdir(rootdir)



