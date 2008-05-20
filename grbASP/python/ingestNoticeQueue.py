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

def forwardErrorMessage(msg):
    preamble = ("Subject: ingestNoticeQueue error\n" +
                "Exception raised in processing the GCN email text:\n")
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    fromaddr = 'glastgcn@slac.stanford.edu'
    toaddr = 'jchiang@slac.stanford.edu'
    mail.sendmail(fromaddr, toaddr, "%s%s" % (preamble, msg))
    mail.quit()

archive_path = "/afs/slac/g/glast/ground/ASP/GCN_Archive"

os.chdir(sys.argv[1])

notices = glob.glob('tmp*')

for notice in notices:
    try:
        my_notice = GcnNoticeEmail(open(notice).readlines())
        my_notice.writeArchive(archive_path)
        packet = Packet(notice)
#        registerWithDatabase(packet)
        os.remove(notice)
    except Exception, msg:
        message = msg + ("\nnotice file %s" % notice)
        forwardErrorMessage(message)
