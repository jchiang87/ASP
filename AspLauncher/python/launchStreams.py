"""
@file launchStreams.py

@brief For each downlink emitted by L1Proc, check for the availability
of L1 data for the next scheduled instance of each task and launch
each one if the required data are available.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from checkLevelOneFiles import providesCoverage
from PipelineCommand import PipelineCommand, _asp_path
from FileStager import FileStager

_version = os.path.split(os.environ['PGWAVEROOT'])[-1]
_pgwaveRoot = os.path.join(_asp_path, 'ASP', 'pgwave', _version)
_datacatalog_imp = os.environ['datacatalog_imp']

def launch_pgwave(interval, frequency, tstart, tstop, folder, output_dir,
                  debug=False):
    args = {'logicalPath' : folder,
            'interval' : interval,
            'frequency' : frequency,
            'TSTART' : tstart,
            'TSTOP' : tstop,
            'OUTPUTDIR' : output_dir,
            'CATDIR' : '/nfs/farm/g/glast/u33/tosti/october/catdir',
            'PGWAVEROOT' : _pgwaveRoot,
            'datacatalog_imp' : _datacatalog_imp}
    command = PipelineCommand('PGWave', args)
    command.run(debug=debug)

def get_interval():
    """Read the environment variables set by the AspLauncher task
    for each frequency of source monitoring to get the start and
    stop times and interval number.
    """
    return (int(os.environ['interval']), 
            os.environ['frequency'],
            int(os.environ['nMetStart']), 
            int(os.environ['nMetStop']))

def createSubDir(interval, frequency, root_output_dir):
    subdir = "%05i" % interval
    os.chdir(root_output_dir)
    newdir = os.path.join(root_output_dir, frequency)
    if not os.path.isdir(newdir):
        os.mkdir(newdir)
        os.system('chmod o+w %s ' % newdir)
    newdir = os.path.join(root_output_dir, frequency, subdir)
    if not os.path.isdir(newdir):
        os.mkdir(newdir)
        os.system('chmod o+w %s ' % newdir)
    return newdir    

if __name__ == '__main__':
    folder = os.environ['folder']
    currentDir = os.getcwd()
    min_frac = float(os.environ['minimum_coverage'])
    process_id = os.environ['PIPELINE_PROCESSINSTANCE']

    #
    # Stage to local /scratch area and clean up on exit
    #
    fileStager = FileStager(os.path.join('AspLauncher', process_id),
                            cleanup=True)

    debug = False

    os.chdir(currentDir)
    interval, frequency, tstart, tstop = get_interval()
    if providesCoverage(tstart, tstop, min_frac, 
                        'Ft1FileList', 'Ft2FileList', 
                        fileStager=fileStager):
        if frequency in ('daily', 'weekly'):
            createSubDir(interval, frequency, os.environ['DRPOUTPUTDIR'])
        output_dir = createSubDir(interval, frequency,
                                  os.environ['PGWAVEOUTPUTDIR'])
        launch_pgwave(interval, frequency, tstart, tstop, folder, 
                      output_dir, debug=debug)
