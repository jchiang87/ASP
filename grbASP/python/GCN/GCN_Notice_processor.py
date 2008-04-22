#!/usr/bin/env python
"""
@brief Redirect GCN Notices to my account.  Write GCN messages to files,
indexed by the notice type and TRIGGER_NUM fields.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import sys
import smtplib

class GcnNoticeEmail(object):
    def __init__(self, lines):
        self.lines = []
        body = False
        for line in lines:
            if line.find('From:') == 0:
                continue
            if line.find("Date: ") == 0:
                self.date = line
            if line.find("Subject: GCN") == 0:
                self.subject = line
                self.notice_type = line.split("/")[-1].strip()
            if line.find("TITLE:") == 0:
                self.title = line.strip().split(":")[-1].strip()
                body = True
            if line.find("TRIGGER_NUM:") == 0:
                # This line combines the trigger number and
                # sequence/segment number and does not have canonical
                # form, so we have this ugly parsing code:
                trig_value = line[12:].split()[0].split(',')[0]
                self.trignum = int(trig_value)
            if body:
                self.lines.append(line)
    def write(self, path):
        output_dir = os.path.join(path, self.notice_type)
        try:
            os.mkdir(output_dir)
        except OSError:
            # Assume the directory already exists.
            pass
        os.system("chmod go+rwx %s" % output_dir)
        outfile = os.path.join(output_dir, "%i" % self.trignum)
        output = open(outfile, 'a')
        output.write("%s" % self.date)
        output.write("%s\n" % self.subject)
        for line in self.lines:
            output.write('%s' % line)
            pass
        delimiter = '-'*80
        output.write(delimiter + '\n')
        output.close()
        os.chmod(outfile, 0666)
    def resend(self, recipients):
        mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
        fromaddr = 'glastgcn@slac.stanford.edu'
        message = ''.join(self.lines)
        message = self.subject + "\n" + message
        message += "\nThis message resent by GCN_Notice_processor.py\n"
        for toaddr in recipients:
            mail.sendmail(fromaddr, toaddr, message)
        mail.quit()

def forwardErrorMessage(msg):
    preamble = ("Subject: GCN_Notice_processor error\n" +
                "Exception raised in processing the GCN email text:\n")
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    fromaddr = 'glastgcn@slac.stanford.edu'
    toaddr = 'jchiang@slac.stanford.edu'
    mail.sendmail(fromaddr, toaddr, "%s%s" % (preamble, msg))
    mail.quit()

if __name__ == '__main__':
    path = '/nfs/farm/g/glast/u33/jchiang/GCN_Archive'

    try:
        my_notice = GcnNoticeEmail(sys.stdin.readlines())
        my_notice.write(path)
    except Exception, msg:
        forwardErrorMessage(msg)

    try:
        my_notice.resend(('jchiang@slac.stanford.edu',))
    except Exception, msg:
        forwardErrorMessage(msg)
