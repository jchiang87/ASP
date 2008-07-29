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
    def __init__(self, subject):
        self.message = StringIO.StringIO()
        self.writer = MimeWriter.MimeWriter(self.message)
        self.writer.addheader('Subject', subject)
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
