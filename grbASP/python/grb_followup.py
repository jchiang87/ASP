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

def promptGrbs():
    sql = "select * from GRB where L1_DATA_AVAILABLE = 0"
    def cursorFunc(cursor):
        notices = {}
        for item in cursor:
            grb_id = item[0]
            notices[grb_id] = GcnNotice(grb_id)
        return notices
    return apply(sql, cursorFunc)

def afterglows():
    sql = "select * from GRB where L1_DATA_AVAILABLE = 1 AND ANALYSIS_VERSION = 0"
    def cursorFunc(cursor):
        notices = {}
        for item in cursor:
            grb_id = item[0]
            notices[grb_id] = GcnNotice(grb_id)
            notices[grb_id].ag_time = item[6] + item[-3]
        return notices
    return apply(sql, cursorFunc)
            
def launch_refinement_streams(notices):
    for grb_id in notices:
        grb_met = notices[grb_id].start_time
        grb_name = notices[grb_id].Name
        config = grbAspConfig.find(grb_met)
        dt = config.TIMEWINDOW
        args = {'GCN_NOTICE' : 'None',
                'GRB_ID' : grb_id,
                'OUTPUTDIR' : os.path.join(os.environ['OUTPUTDIR'], grb_name),
                'GRBASPROOT' : os.environ['GRBASPROOT'],
                'TSTART' : grb_met - dt,
                'TSTOP' : grb_met + dt,
                'logicalPath' : os.environ['logicalPath']}
        command = PipelineCommand('GRB_refinement_launcher', args)
        command.run()

def launch_afterglow_streams(notices):
    for grb_id in notices:
        ag_time = notices[grb_id].ag_time
        grb_name = notices[grb_id].Name
        config = grbAspConfig.find(ag_time)
        dt = config.AGTIMESCALE
        args = {'logicalPath' : os.environ['logicalPath'],
                'TSTART' : int(ag_time),
                'TSTOP' : int(ag_time + dt),
                'OUTPUTDIR' : os.path.join(os.environ['OUTPUTDIR'], grb_name),
                'GRBASPROOT' : os.environ['GRBASPROOT']}
        command = PipelineCommand('GRB_afterglow_launcher', args)
        command.run()

def handle_unprocessed_events():
    prompt_notices = promptGrbs()
    launch_refinement_streams(prompt_notices)

    afterglow_events = afterglows()
    launch_afterglow_streams(afterglow_events)
