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
#_ST_path = "/nfs/farm/g/glast/u09/builds/rh9_gcc32/ScienceTools/ScienceTools-LATEST1.1537"
_ST_path = "/nfs/farm/g/glast/u06/jchiang/ST"
_ASP_path = "/nfs/farm/g/glast/u33/jchiang/ASP"
#_ASP_path = os.path.join(os.path.split(os.environ['PYASPROOT'])[:-3])
#_ASP_path = "/nfs/slac/g/svac/focke/ASP/code"
_pyASP_version = os.environ['PYASPROOT'].split(os.path.sep)[-1]
_pyASP_root = os.path.join(_ASP_path, "ASP", "pyASP", _pyASP_version)
_asp_python = "/usr/local/bin/python"

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
    output.write("PATH=%s:${PATH}; export PATH\n" % os.path.join(_ST_path, 'bin'))
    output.write("source %s\n" % os.path.join(_pyASP_root, 'cmt', 'setup.sh'))
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
        if sys.argv[1:]:
            wrapperGenerator(sys.argv[1])
        else:
            standard_scripts = ('BlindSearch.py',
                                'extractLatData.py',
                                'refinePosition.py',
                                'tsMap.py',
                                'LatGrbSpectrum.py',
                                'afterglowData.py',
                                'afterglowLivetimeCube.py',
                                'afterglowDiffResps.py',
                                'afterglowExpMap.py', 
                                'combineExpMaps.py',
                                'afterglowAnalysis.py',
                                'getIntervalData.py',
                                'diffuseResponses.py',
                                'livetimecube.py',
                                'getRoiData.py',
                                'drpExpMap.py', 
                                'combineDrpExpMaps.py',
                                'sourceAnalysis.py',
                                'fitEnergyBand.py',
                                'countsMap.py',
                                'flare_livetimecube.py',
                                'sourceMap.py',
                                'modelMap.py',
                                'flareSearch.py')
            for script in standard_scripts:
                wrapperGenerator(script)
