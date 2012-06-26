#!/usr/bin/sh

# Note this is site-dependent!  But expectation is that this stuff will
# only be run on SLAC linux.  All site-dependent stuff belongs in this file
# or in asp_presetup.sh.

export TNS_ADMIN=/u/gl/glast/oracle/admin
#export ORACLE_HOME=/afs/slac/package/oracle/d/linux/11.1.0
export ORACLE_HOME=/afs/slac.stanford.edu/package/oracle/f/11.1.0/amd64_linux26/11.1.0

pipeline_config_root=/afs/slac.stanford.edu/g/glast/ground/PipelineConfig
asp_db_config=${pipeline_config_root}/ASP/db_config

asp_python_path=${pipeline_config_root}/ASP/python/lib/python2.6_x86_64/site-packages
asp_lib_path=${pipeline_config_root}/ASP/lib
GPLtools_path=${pipeline_config_root}/GPLtools/asp/python

export LD_LIBRARY_PATH=${ORACLE_HOME}/lib:${LD_LIBRARY_PATH}:${asp_lib_path}

export PYTHONPATH=${asp_python_path}:${GPLtools_path}:${PYTHONPATH}

export PFILES=${PFILES}:${BASE_DIR}/syspfiles
