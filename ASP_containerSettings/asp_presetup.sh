#!/usr/bin/sh

# Note this is site-dependent!  But expectation is that this stuff will
# only be run on SLAC linux.  All site-dependent stuff belongs in this file
# or in asp_postsetup.sh.

pipeline_config_root=/afs/slac.stanford.edu/g/glast/ground/PipelineConfig/
ftools_setup=${pipeline_config_root}ASP/headas-config-noric024835.sh

export PFILES=".;"

source ${ftools_setup}

#export GLAST_EXT=/afs/slac.stanford.edu/g/glast/ground/GLAST_EXT/redhat4-i686-32bit-gcc34
#export GLAST_EXT=/afs/slac.stanford.edu/g/glast/ground/GLAST_EXT/redhat5-x86_64-64bit-gcc41
export GLAST_EXT=/afs/slac.stanford.edu/g/glast/ground/GLAST_EXT/redhat6-x86_64-64bit-gcc44
