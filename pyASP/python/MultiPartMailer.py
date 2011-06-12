"""
@brief Class to handle multiple-part email messages, especially with
multiple image attachments.  Based on chapter 10.9 of Python Cookbook.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import smtplib

class MultiPartMailer(object):
    def __init__(self, subject, reply_to=None):
        self.message = MIMEMultipart()
        self.message['Subject'] = subject
        if reply_to is not None:
            self.message['Reply-to'] = reply_to
    def add_text(self, text):
        txt = MIMEText(text)
        self.message.attach(txt)
    def add_image(self, image_file):
        fp = open(image_file, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        self.message.attach(img)
    def send(self, sender, recipients):
        mailer = smtplib.SMTP('smtpunix.slac.stanford.edu')
        mailer.sendmail(sender, recipients, self.message.as_string())
        mailer.close()
    def finish(self):
        pass

if __name__ == '__main__':
    print "sending test message"
    mailer = MultiPartMailer('Test message', 'jchiang@slac.stanford.edu')
    mailer.add_text("hello, world")
    mailer.send("glastgcn@slac.stanford.edu", ('jchiang@slac.stanford.edu',))
