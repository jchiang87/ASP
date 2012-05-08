"""
@brief Function to emit files to GSSC via FASTCopy.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

def fastCopy(outfile, dest=None):
    command = "eval `/afs/slac/g/glast/isoc/flightOps/rhel5_gcc41/ISOC_PROD/bin/isoc env --add-env=flightops`; FASTCopy.py "
    if dest in ('GSSC', 'ISOC'):
        command += "--send %s " % dest
    command += outfile
    print command
    os.system(command)

if __name__ == '__main__':
    fastCopy('foo')
