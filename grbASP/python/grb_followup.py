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
from PipelineCommand import PipelineCommand, resolve_nfs_path
from GcnNotice import GcnNotice
from databaseAccess import *
from GrbAspConfig import grbAspConfig
from date2met import date2met
import time
import databaseAccess as dbAccess

grbasproot = resolve_nfs_path(os.environ['INST_DIR'])

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
    print "dbAccess:", dbAccess.asp_default
    print "inside launch_refinement_streams:"
    for grb_id in notices:
        print grb_id
        grb_met = notices[grb_id].start_time
        grb_name = notices[grb_id].Name
        try:
            print grb_met
            print grb_name
            config = grbAspConfig.find(grb_met)
        except RuntimeError:
            print "error finding notice time in GRB_ASP_CONFIG table"
            grb_met = grb_id
            config = grbAspConfig.find(grb_met)
        dt = config.TIMEWINDOW
        args = {'GCN_NOTICE' : 'None',
                'GRB_ID' : grb_id,
                'OUTPUTDIR' : os.path.join(output_dir, `grb_id`),
                'GRBASPROOT' : grbasproot,
                'TSTART' : grb_met - dt,
                'TSTOP' : grb_met + dt,
                'folder' : os.environ['folder'],
                'datacatalog_imp' : os.environ['datacatalog_imp']}
        command = PipelineCommand('GRB_refinement_launcher', args)
        command.run()
        time.sleep(30)

def launch_afterglow_streams(output_dir):
    notices = afterglows()
    for grb_id in notices:
        ag_time = notices[grb_id].ag_time
        grb_name = notices[grb_id].Name
        print "launching afterglow for ", grb_name
        config = grbAspConfig.find(ag_time)
        dt = config.AGTIMESCALE
        args = {'folder' : os.environ['folder'],
                'GRB_ID' : grb_id,
                'TSTART' : int(ag_time),
                'TSTOP' : int(ag_time + dt),
                'OUTPUTDIR' : os.path.join(output_dir, `grb_id`),
                'GRBASPROOT' : grbasproot,
                'datacatalog_imp' : os.environ['datacatalog_imp']}
        command = PipelineCommand('GRB_afterglow_launcher', args)
        command.run()
        time.sleep(30)

def purge_old_notices():
    """Unprocessed Notices older than 1 week either have trigger times
    during an SAA passage or do not have data from the MOC, so skip
    prompt processing by setting the ASP_PROCESSING_LEVEL to 1.
    Notices at processing level 1 that are older than 8 days should
    have had afterglow processing finished; if not, skip them by
    setting ASP_PROCESSING_LEVEL to 2.
    """
    if os.environ['PIPELINESERVER'] == 'DEV':
        return
    right_now = int(date2met())
    sql = ("update GRB set ASP_PROCESSING_LEVEL=2 where GRB_ID<%i" 
           % (right_now - 86400*7) + " and ASP_PROCESSING_LEVEL=0")
    print "purging old, unprocessed notices:"
    print sql
    print ""
    apply(sql)

    sql = ("update GRB set ASP_PROCESSING_LEVEL=2 where GRB_ID<%i"
           % (right_now - 86400*8) + " and ASP_PROCESSING_LEVEL=1")
    print "purging old, unprocessed notices:"
    print sql
    print ""
    apply(sql)

def handle_unprocessed_events(output_dir):
    purge_old_notices()
#    launch_refinement_streams(output_dir)
#    launch_afterglow_streams(output_dir)
