"""
@brief Generate bash wrapper scripts to set the environment for
running the pyASP Python scripts.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import sys

_ftools_setup= "/afs/slac/g/glast/ground/PipelineConfig/ASP/headas-config-noric024835.sh"
#_ST_path = "/nfs/farm/g/glast/u09/builds/rh9_gcc32/ScienceTools/ScienceTools-LATEST1.1537"
_ST_path = "/nfs/farm/g/glast/u06/jchiang/ST"
_ASP_path = "/nfs/farm/g/glast/u33/jchiang/ASP"
_pyASP_version = "v0r1"
_pyASP_root = os.path.join(_ASP_path, "pyASP", _pyASP_version)
_asp_python = "/usr/local/bin/python"

if not sys.argv[1:]:
    print "usage: %s <python script name>" % sys.argv[0]
    sys.exit(1)

prefix = sys.argv[1].split(".py")[0]
pyScript = os.path.abspath(sys.argv[1])

output = open(prefix + ".sh", "w")
output.write("#!/usr/local/bin/bash\n")
output.write("CMTSITE=SLAC_UNIX; export CMTSITE\n")
output.write("CMTVERSION=v1r16p20040701; export CMTVERSION\n")
output.write("CMTBASE=/afs/slac.stanford.edu/g/glast/applications/CMT; export CMTBASE\n")
output.write("CMTROOT=/afs/slac.stanford.edu/g/glast/applications/CMT/v1r16p20040701; export CMTROOT\n")
output.write("CMTBIN=Linux; export CMTBIN\n")
output.write("CMTCONFIG=rh9_gcc32; export CMTCONFIG\n")
output.write("CMTPATH=%s; export CMTPATH\n" %
             os.pathsep.join((_ST_path, _ASP_path)))
output.write("source %s\n" % _ftools_setup)
output.write("GLAST_EXT=/afs/slac/g/glast/ground/GLAST_EXT/rh9_gcc32; export GLAST_EXT\n")
output.write("PATH=%s:${PATH}; export PATH\n" % os.path.join(_ST_path, 'bin'))
output.write("source %s\n" % os.path.join(_pyASP_root, 'cmt', 'setup.sh'))
output.write('%s %s\n' % (_asp_python, pyScript))
output.close()
os.system('chmod +x %s' % (prefix + '.sh',))