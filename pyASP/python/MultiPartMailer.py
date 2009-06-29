"""
@brief Class to handle multiple-part email messages, especially with
multiple image attachments.  Based on chapter 10.9 of Python Cookbook.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import MimeWriter
import base64
import StringIO
import smtplib
import socket
import time

class MultiPartMailer(object):
    def __init__(self, subject, reply_to=None):
        self.message = StringIO.StringIO()
        self.writer = MimeWriter.MimeWriter(self.message)
        self.writer.addheader('Subject', subject)
        if reply_to is not None:
            self.writer.addheader('Reply-to', reply_to)
        self.writer.startmultipartbody('mixed')
    def add_text(self, text):
        part = self.writer.nextpart()
        body = part.startbody('text/plain')
        body.write(text)
    def add_image(self, image_file):
        file_ext = image_file.split('.')[-1]
        part = self.writer.nextpart()
        part.addheader('Content-Transfer-Encoding', 'base64')
        body = part.startbody('image/%s; name=%s' % (file_ext, image_file))
        base64.encode(open(image_file, 'rb'), body)
    def finish(self):
        self.writer.lastpart()
    def send(self, sender, recipients):
        mailer = smtplib.SMTP('smtpunix.slac.stanford.edu')
        mailer.sendmail(sender, recipients, self.message.getvalue())
        mailer.close()

if __name__ == '__main__':
    print "sending test message"
    mailer = MultiPartMailer('Test message', 'jchiang@slac.stanford.edu')
    mailer.add_text("hello, world")
    mailer.send("glastgcn@slac.stanford.edu", ('jchiang@slac.stanford.edu',))
