"""
@brief Functions in this script check for unhandled prompt and
afterglow GRB events and then launches the conditional launcher tasks
that execute the real tasks only if the L1 data are available.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from PipelineCommand import PipelineCommand
from GcnNotice import GcnNotice
from databaseAccess import *
from GrbAspConfig import grbAspConfig

#
# For nfs mounted disks, <package>ROOT is resolved to the
# process-dependent mount point, so we must rebuild the path using
# ASP_PATH
#
grbasproot = os.path.join(os.environ['ASP_PATH'], 'ASP', 'grbASP',
                          os.path.split(os.environ['GRBASPROOT'])[-1])

def promptGrbs():
    sql = "select GRB_ID from GRB where GCAT_FLAG=0 and ASP_PROCESSING_LEVEL=0"
    def cursorFunc(cursor):
        notices = {}
        for item in cursor:
            grb_id = item[0]
            notices[grb_id] = GcnNotice(grb_id)
        return notices
    return apply(sql, cursorFunc)

def afterglows():
    sql = ("select GRB_ID, LAT_LAST_TIME " +
           "from GRB where GCAT_FLAG=0 and ASP_PROCESSING_LEVEL=1")
    def cursorFunc(cursor):
        notices = {}
        for item in cursor:
            grb_id = item[0]
            notices[grb_id] = GcnNotice(grb_id)
            try:
                notices[grb_id].ag_time = item[1]
            except TypeError:
                # kluge. LAT_LAST_TIME is null, so infer refinement
                # task has not successfully run for this burst.
                del notices[grb_id]
        return notices
    return apply(sql, cursorFunc)
            
def launch_refinement_streams(output_dir):
    notices = promptGrbs()
    for grb_id in notices:
        grb_met = notices[grb_id].start_time
        grb_name = notices[grb_id].Name
        config = grbAspConfig.find(grb_met)
        dt = config.TIMEWINDOW
        args = {'GCN_NOTICE' : 'None',
                'GRB_ID' : grb_id,
                'OUTPUTDIR' : os.path.join(output_dir, `grb_id`),
                'GRBASPROOT' : grbasproot,
                'TSTART' : grb_met - dt,
                'TSTOP' : grb_met + dt,
                'logicalPath' : os.environ['logicalPath'],
                'ST_INST' : os.environ['ST_INST'],
                'datacatalog_imp' : os.environ['datacatalog_imp']}
        command = PipelineCommand('GRB_refinement_launcher', args)
        command.run()

def launch_afterglow_streams(output_dir):
    notices = afterglows()
    for grb_id in notices:
        ag_time = notices[grb_id].ag_time
        grb_name = notices[grb_id].Name
        print "launching afterglow for ", grb_name
        config = grbAspConfig.find(ag_time)
        dt = config.AGTIMESCALE
        args = {'logicalPath' : os.environ['logicalPath'],
                'GRB_ID' : grb_id,
                'TSTART' : int(ag_time),
                'TSTOP' : int(ag_time + dt),
                'OUTPUTDIR' : os.path.join(output_dir, `grb_id`),
                'GRBASPROOT' : grbasproot,
                'ST_INST' : os.environ['ST_INST'],
                'datacatalog_imp' : os.environ['datacatalog_imp']}
        command = PipelineCommand('GRB_afterglow_launcher', args)
        command.run()

def handle_unprocessed_events(output_dir):
    launch_refinement_streams(output_dir)
    launch_afterglow_streams(output_dir)
