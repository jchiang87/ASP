"""
@brief Ingest all of the files that were archived by the
GCN_Notice_processor.py.

@author J. Chiang
"""
#
# $Header$
#

import os
import subprocess
import sys
import glob
import smtplib
from ingestEmailNotice import Packet, registerWithDatabase
from GCN_Notice_processor import GcnNoticeEmail
from PipelineCommand import resolve_nfs_path
from GBM_Notice_parser import GBM_Notice_parser

def forwardErrorMessage(msg):
    preamble = ("Subject: ingestNoticeQueue error\n" +
                "Exception raised in processing the GCN email text:\n")
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    fromaddr = 'glastgcn@slac.stanford.edu'
    toaddr = 'jchiang@slac.stanford.edu'
    mail.sendmail(fromaddr, toaddr, "%s%s" % (preamble, msg))
    mail.quit()

#archive_path = "/nfs/farm/g/glast/u52/ASP/GCN_Archive"
archive_path = "/nfs/farm/g/glast/u41/ASP/GCN_Archive"
#archive_path = "/afs/slac/g/glast/ground/links/data/ASP/GCN_Archive"

if sys.argv[1:]:
    os.chdir(sys.argv[1])
else:
    os.chdir(os.path.join(archive_path, "NOTICE_QUEUE"))

notices = glob.glob('tmp*')

skipped_notice_types = ('SWIFT_SC_SLEW', 'SWIFT_UVOT_POSITION_NACK')

for notice in notices:
    try:
        #
        # Fill FERMI_GCN_NOTICE_INFO table
        #
        try:
            gbm_parser = GBM_Notice_parser(open(notice))
            gbm_parser.update_tables()
        except:
            pass
        #
        # Fill GCNNOTICES table
        #
        packet = Packet(notice)
        if ((packet.trigger_num==99999 and packet.mission.lower()=='fermi') or
            (packet.notice_type in skipped_notice_types)):
            pass
        else:
            my_notice = GcnNoticeEmail(open(notice).readlines())
            outfile = my_notice.writeArchive(archive_path)
            registerWithDatabase(packet, resolve_nfs_path(outfile))
        #
        # clean-up tmp file if all is successful.
        #
        os.remove(notice)
    except Exception, msg:
        os.rename(notice, "_" + notice)
        message = str(msg) + ("\nfor notice file %s" % notice)
        forwardErrorMessage(message)

#try:
#    command = "/afs/slac/g/glast/groups/grb/Weekly_FT2/GCN_off_axis_plots/plot_offaxis_angles.sh"
#    subprocess.call(command, shell=True)
#except Exception, msg:
#    forwardErrorMessage(msg)
