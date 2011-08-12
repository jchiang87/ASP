#  setup for point fit 
# $Header$
from  pointlike_defaults import *
import os

# specify file or files with photon data
Data.files = [r'f:\glast\data\flight\ft1_august_reproc.fits']

#specify a text file with starting positions
sourcelistfile = r'D:\common\pointfind\strong\high_confidence.txt'


# set up galactic diffuse to use
Diffuse.file = os.path.join(os.environ['GLAST_EXT'],'extFiles','v0r7','galdiffuse', 'GP_gamma.fits')
Diffuse.exposure=3e10/12.  # scale from 3e10 for a year.

#file name to write output (text format) to
outfile = 'output.txt'

# this function, if it exists, will be called at the end of the job
def finish():
  print 'Finishing:'
  if not os.path.exists(outfile):
    print 'job failed? no output'
    return
  else:
    print 'wrote to file %s' % outfile
    # can do other processing here
      