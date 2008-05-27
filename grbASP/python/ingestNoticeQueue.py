"""
@brief Ingest all of the files that were archived by the
GCN_Notice_processor.py.

@author J. Chiang
"""
#
# $Header$
#

import os
import sys
import glob
import smtplib
from ingestEmailNotice import Packet, registerWithDatabase
from GCN_Notice_processor import GcnNoticeEmail
from PipelineCommand import resolve_nfs_path

def forwardErrorMessage(msg):
    preamble = ("Subject: ingestNoticeQueue error\n" +
                "Exception raised in processing the GCN email text:\n")
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    fromaddr = 'glastgcn@slac.stanford.edu'
    toaddr = 'jchiang@slac.stanford.edu'
    mail.sendmail(fromaddr, toaddr, "%s%s" % (preamble, msg))
    mail.quit()

#archive_path = "/afs/slac/g/glast/ground/ASP/GCN_Archive"
archive_path = "/nfs/farm/g/glast/u33/ASP/GCN_Archive"

if sys.argv[1:]:
    os.chdir(sys.argv[1])
else:
    os.chdir("/nfs/farm/g/glast/u33/ASP/GCN_Archive/NOTICE_QUEUE")

notices = glob.glob('tmp*')

for notice in notices:
    try:
        packet = Packet(notice)
        if packet.trigger_num==99999 and packet.mission=='GLAST':
            pass
        else:
            my_notice = GcnNoticeEmail(open(notice).readlines())
            outfile = my_notice.writeArchive(archive_path)
            registerWithDatabase(packet, resolve_nfs_path(outfile))
        os.remove(notice)
    except Exception, msg:
        os.rename(notice, "_" + notice)
        message = str(msg) + ("\nfor notice file %s" % notice)
        forwardErrorMessage(message)
