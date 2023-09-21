#!/usr/bin/env python
"""
@brief Redirect GCN Notices.  Write GCN messages to files, indexed by
the mission and TRIGGER_NUM fields.  Since this is executed from a
Sparc via procmail, it must be pure python, and cannot use third-party
python modules.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import sys
import smtplib
import tempfile

def round(x):
    frac = x % 1
    if frac > 0.5:
        return int(x) + 1
    return int(x)

def gregorianDate(TJD, SOD):
    """ Convert TJD, SOD to Gregorian Dates (year, month, day, hours).
    This inscrutable code is stolen from astro::JulianDate.cxx
    """
    julianDate = TJD + 2440000.5 + SOD/8.64e4
    
    jd = int(julianDate)
    frac = julianDate - jd + 0.5

    if frac >= 1:
        frac -= 1.
        jd += 1

    hr = frac*24
    l = int(jd +  + 68569)
    n = 4*l / 146097L
    l = l - (146097*n + 3L) / 4
    yr = 4000*(l+1) / 1461001
    l = l - 1461*yr / 4 + 31
    mn = 80*l / 2447
    day = l - 2447*mn / 80
    l = mn/11
    mn = mn + 2 - 12*l
    yr = 100*(n-49) + yr + l
    
    return yr, mn, day, hr

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
                # parse subject line to determine notice type and
                # mission name
                self.subject = line
                self.notice_type = line.split("/")[-1].strip()
                self.mission_name = self.notice_type.split("_")[0]
            if line.find("TITLE:") == 0:
                self.title = line.strip().split(":")[-1].strip()
                body = True
            if line.find("TRIGGER_NUM:") == 0:
                # This line combines the trigger number and
                # sequence/segment number and does not have canonical
                # form, so we have this ugly parsing code:
                trig_value = line[12:].split()[0].split(',')[0]
                try:
                    self.trignum = int(trig_value)
                except ValueError:
#                    # Omit leading non-numeric character from LVC notice
#                    # TRIGGER_NUM values
#                    self.trignum = int(trig_value[1:])
                    self.trignum = trig_value
            if (line.find('GRB_DATE:') == 0 or
                line.find('IMG_START_DATE:') == 0 or
                line.find('POINT_DATE:') == 0):
                self.TJD = int(line.split()[1])
            if (line.find('GRB_TIME:') == 0 or
                line.find('IMG_START_TIME:') == 0 or
                line.find('POINT_TIME:') == 0):
                self.SOD = int(float(line.split()[1]))
            if body:
                self.lines.append(line)
    def writeArchive(self, path):
        """Archive the notice under path, in a subdirectory given by the
        mission name and in a filename given by the trigger number."""
        output_dir = os.path.join(path, self.mission_name)
        try:
            os.mkdir(output_dir)
            os.system("chmod go+rwx %s" % output_dir)
        except OSError:
            # Assume the directory already exists and is write-accessible.
            pass
        outfile = os.path.join(output_dir, "%i" % self.trignum)
        self.writeFile(outfile, add_delimiter=True)
        return outfile
    def grbName(self):
        year, month, day, hour = gregorianDate(self.TJD, self.SOD)
        #
        # Add a leap second for Dec 31, 2005 event. Another will be needed
        # after Dec 31, 2008
        #
        hour += 1./3600.
        grb_name = "GRB%02i%02i%02i%03i" % (year % 2000, month, day, 
                                            round(self.SOD/86400.*1000.))
        return grb_name
    def writeFile(self, outfile, add_delimiter=False):
        output = open(outfile, 'a')
        output.write("%s" % self.date)
        output.write("%s\n" % self.subject)
        for line in self.lines:
            output.write('%s' % line)
            pass
        if add_delimiter:
            delimiter = '-'*80
            output.write(delimiter + '\n')
        output.close()
        os.chmod(outfile, 0666)
    def resend(self, recipients):
        mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
        fromaddr = 'glastgcn@slac.stanford.edu'
        message = ''.join(self.lines)
        self.subject = self.subject.strip() + " - %s" % self.grbName()
        message = self.subject + "\n\n" + message
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
    import os, sys
#    path = '/nfs/farm/g/glast/u52/ASP/GCN_Archive'
    path = '/afs/slac/g/glast/ground/links/data/ASP/GCN_Archive'
    queue_path = os.path.join(path, "NOTICE_QUEUE")

    try:
        try:
            my_notice = GcnNoticeEmail(sys.stdin.readlines())
        except Exception, msg:
            raise RuntimeError("Error in GcnNoticeEmail constructor: " + msg)
        try:
            fd, queued_file = tempfile.mkstemp(dir=queue_path)
            os.close(fd)
        except Exception, msg:
            raise RuntimeError("Error in creating tmp file name: " + msg)
        try:
            my_notice.writeFile(queued_file)
        except Exception, msg:
            raise RuntimeError("Error writing to NOTICE_QUEUE: " + msg)
        os.chdir(queue_path)
        os.system('chmod 666 *')
    except Exception, msg:
        forwardErrorMessage(msg)

    try:
        if ((my_notice.mission_name.lower() != "fermi" or
             my_notice.trignum != 99999)):
            pass
#            my_notice.resend(('jchiang@slac.stanford.edu',
#                              'balist@glast.stanford.edu'))
    except Exception, msg:
        forwardErrorMessage(msg)
