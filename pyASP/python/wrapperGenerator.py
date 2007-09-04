"""
@brief Generate bash wrapper scripts to set the environment for
running the pyASP Python scripts.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

_ftools_setup= "/afs/slac/g/glast/ground/PipelineConfig/ASP/headas-config-noric024835.sh"
_pyfits_path = "/afs/slac/g/glast/ground/PipelineConfig/ASP/pyfits/lib"
_ST_path = "${ST_INST}"
_ASP_path = "${ASP_PATH}"
#
# We need to build _ASP_root this way, rather than using
# os.environ['ASPROOT'] directly, since nfs mount points are not
# persistent from process to process
#
_ASP_version = os.environ['ASPROOT'].split(os.path.sep)[-1]
_ASP_root = os.path.join(_ASP_path, "ASP", _ASP_version)
_asp_python = "/usr/bin/env python"

def wrapperGenerator(scriptName):
    prefix = scriptName.split(".py")[0]
    pyScript = os.path.abspath(scriptName)
    outfile = os.path.join(os.environ['PYASPROOT'], os.environ['BINDIR'],
                           prefix + ".sh")
    output = open(outfile, "w")
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
    output.write("PATH=%s:${PATH}; export PATH\n" 
                 % os.path.join(_ST_path, 'bin'))
    output.write("source %s\n" % os.path.join(_ASP_root, 'cmt', 'setup.sh'))
    output.write("PYTHONPATH=%s:${PYTHONPATH}; export PYTHONPATH\n" 
                 % _pyfits_path)
    output.write('exec %s %s\n' % (_asp_python, pyScript))
    output.close()
    os.system('chmod +x %s' % outfile)

if __name__ == '__main__':
    import sys
    try:
        sys.argv[1:].index('-h')
        print "usage: %s [<Python script name>]" % sys.argv[0]
        sys.exit(1)
    except ValueError:
        wrapperGenerator(sys.argv[1])
