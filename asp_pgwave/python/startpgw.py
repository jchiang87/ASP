import os
#from createPgwStreams import *


pgwRoot = lambda x : os.path.join(os.environ['PGWAVEROOT'], x)

os.environ['ASP_PATH'] = '/nfs/farm/g/glast/u33/tosti/myASP'

os.environ['ST_INST'] ='/nfs/farm/g/glast/u30/builds/rh9_gcc32/ScienceTools/ScienceTools-v9r2'
#os.environ['OUTPUTDIR'] = rootdir
os.environ['PIPELINESERVER'] = 'DEV'
os.environ['BINDIR']='rh9_gcc32'


#from pgw2fits import *
#from runsrcid import *

outdir=os.getcwd()
os.environ['OUTPUTDIR'] = outdir
from createPgwStreams import *
down='down1'
try:
        os.mkdir(down)
except OSError:
        pass
os.system('chmod 777 %s ' % down)
output_dir = os.path.abspath(down)

pgwStreams(1, output_dir)
#os.chdir(os.environ['OUTPUTDIR']
#infile='prime4h.fits'
#runpgw(infile)
#	pgw2fits(os.environ['PGWOUTPUTLIST'],1)
#	runsrcid (os.environ['PGWOUTPUTFITSLIST'],0.30)
#	os.system('rm temp.fits')	

