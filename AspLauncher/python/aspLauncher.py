"""
@file aspLauncher.py

@brief This script queries the TIMEINTERVALS db table and calculates
the next set of intervals for which the associated ASP tasks are
launched.  The wrapped version of this script is intended to be
launched as a subprocess of L1Proc.

Two environment variables need to be provided:

nDownlink = Data delivery ID of the current L1Proc instance
folder = Logical folder in the dataCatalog that contains the FT1/2 data

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from createGrbStreams import blindSearchStreams
import databaseAccess as dbAccess

def resolve_nfs_path(path):
    tokens = path.split(":")
    for i in range(len(tokens)):
        if tokens[i].find('g.glast.'):
            tokens[i] = os.path.join('/nfs/farm/g/glast', 
                                     tokens[i].split('g.glast.')[-1])
    return ":".join(tokens)

if __name__ == '__main__':
    from intervalAccess import unhandledIntervals
    from PipelineCommand import PipelineCommand

    _aspLauncherRoot = resolve_nfs_path(os.environ['ASPLAUNCHERROOT'])

    #
    # Standard output directory for ASP results.  Will this be
    # replaced by a symlink as proposed?
    #
    _output_dir = '/nfs/farm/g/glast/u33/ASP/'

    aspOutput = lambda x : os.path.join(_output_dir, x)

    try:
       os.environ['folder'], os.environ['nDownlink']
    except KeyError:
       os.environ['folder'] = '/Data/OpsSim2/Level1'
       os.environ['nDownlink'] = '80302002'

    print "Using "
    print "DataCatalog folder =", os.environ['folder']
    print "Downlink ID =", os.environ['nDownlink']

    nDownlink = int(os.environ['nDownlink'])
    blindSearchStreams(downlinks=(nDownlink,),
                       logicalPath=os.environ['folder'],
                       grbroot_dir=aspOutput('GRB'),
                       streamId=nDownlink, 
                       datacatalog_imp="datacatalog",
                       debug=False)

    unhandled = unhandledIntervals()
    for offset, frequency in enumerate(unhandled):
       for interval in unhandled[frequency]:
          args = {'folder' : os.environ['folder'],
                  'nDownlink' : nDownlink,
                  'interval' : interval.interval,
                  'frequency' : frequency,
                  'nMetStart' : interval.tstart,
                  'nMetStop' : interval.tstop,
                  'GRBOUTPUTDIR' : aspOutput('GRB'),
                  'DRPOUTPUTDIR' : aspOutput('DRP'),
                  'PGWAVEOUTPUTDIR' : aspOutput('PGWAVE'),
                  'PIPELINESERVER' : 'PROD',
                  'ASPLAUNCHERROOT' : _aspLauncherRoot,
                  'datacatalog_imp' : 'datacatalog'}

          for item in args:
             print item, args[item]
          print "\n*******************\n"
    
          stream_id = interval.tstart + offset
          launcher = PipelineCommand('AspLauncher', args, stream=stream_id)
          launcher.run(debug=False)
