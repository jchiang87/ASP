#!/usr/bin/sh

# Note this is site-dependent!  But expectation is that this stuff will
# only be run on SLAC linux.  All site-dependent stuff belongs in this file
# or in asp_presetup.sh.

export PFILES=".;"
export TNS_ADMIN=/u/gl/glast/oracle/admin
export ORACLE_HOME=/afs/slac/package/oracle/d/linux/11.1.0

pipeline_config_root=/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/
asp_db_config=${pipeline_config_root}ASP/db_config

asp_python_path=${pipeline_config_root}ASP/python/lib/python2.5/site-packages
asp_lib_path=${pipeline_config_root}ASP/lib
GPLtools_path=${pipeline_config_root}GPLtools/asp/python

#export LD_LIBRARY_PATH=${ORACLE_HOME}/lib:${LD_LIBRARY_PATH}:${asp_lib_path}

export PYTHONPATH=${asp_python_path}:${GPLtools_path}:${PYTHONPATH}

# Define these temporarily until we can determine how to set them correctly
# in SCons
# Should not be necessary with facilities 02-18-12 or later
#export CALDB=/afs/slac/g/glast/groups/asp/jrbdev/ST-LATEST-2992/data/caldb/data/glast/lat
#export CALDBCONFIG=/afs/slac/g/glast/groups/asp/jrbdev/ST-LATEST-2992/data/caldb/software/tools/caldb.config
#export CALDBALIAS=/afs/slac/g/glast/groups/asp/jrbdev/ST-LATEST-2992/data/caldb/software/tools/alias_config.fits
