# @brief Script to execute FASTCopy.py on monitored source light curve file
# from ASP.  This must be executed outside of the standard ASP bash wrapper,
# since FASTCopy.py uses an old version of python (2.5) and imports an
# incompatible version of the cx_Oracle module (contra the x86_64 version
# that must be used on the rhel5-64 batch machines.)
#
# @author J. Chiang <jchiang@slac.stanford.edu>
#
# $Header$
#

import os
import glob
import subprocess

os.chdir('/afs/slac/g/glast/ground/links/data/ASP/scratch')

outfile = glob.glob('gll_asp*.fit')
outfile.sort()

command = 'bsub -q short -R rhel50 "eval `/afs/slac/g/glast/isoc/flightOps/rhel5_gcc41/ISOC_PROD/bin/isoc env --add-env=flightops`; FASTCopy.py --send GSSC %s"' % outfile[-1]

print command

subprocess.call(command, shell=True)

if len(outfile) > 2:
    for item in outfile[:-2]:
        os.remove(item)
