"""
@brief Prototype GCN Socket Server.

@author J. Chiang <jchiang@slac.stanford.edu>
@author P. Nolan <Patrick.Nolan@stanford.edu>
"""
#
# $Header$
#

import os
import time
import socket
import array
import sys
import select

from GcnPacket import GcnPacket
from dbAccess import insertGrb, insertGcnNotice, current_date, updateGrb
from createGrbStreams import refinementStreams

try:
    _outputDir = os.environ['OUTPUTDIR']
except:
    _outputDir = os.path.join('GRBASPROOT', 'python', 'GCN', 'output')

def emailNotice(packet, recipients, fromadr="jchiang@slac.stanford.edu"):
    import smtplib
    packet_type = "GCN Packet type %i" % packet.type
    subj = packet_type
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    for address in recipients:
        hdr = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
               % (fromadr, address, subj))
        message = "%s%s" % (hdr, packet)
        mail.sendmail(fromadr, address, message)
    mail.quit()

def noticeGenerator(packet, outfile=None):
    if outfile is None:
        outfile = os.path.join(_outputDir, "GRB%i_Notice.txt" % packet.MET)
    output = open(outfile, "w")
    output.write("TITLE:          GCN NOTICE\n")
    output.write("NOTICE_DATE:    %s\n" % time.asctime())
    output.write("TRIGGER_NUM:    %s\n" % packet.triggerNum)
    output.write("GRB_RA:         %7.3fd (J2000)\n" % packet.RA)
    output.write("GRB_DEC:        %7.3fd (J2000)\n" % packet.Dec)
    output.write("GRB_ERROR:      10.00 [arcmin] \n")
    output.write("GRB_DATE:       %i TJD; \n" % packet.TJD)
    output.write("GRB_TIME:       %.2f SOD \n" % packet.SOD)
    output.close()
    return outfile

class GcnServer(object):
    _IM_ALIVE = 3
    _KILL_SOCKET = 4
    def __init__(self, port=5263, bufsize=4*40):
        self.port = port
        self.bufsize = bufsize
        self.recipients = ["jchiang@slac.stanford.edu"]
    def _listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", self.port))
        self.sock.listen(5)
    def registerWithDatabase(self, packet):
        grb_id = packet.MET
        try:
            insertGrb(grb_id)
        except cx_Oracle.DatabaseError, message:
            print message
            pass
        updateGrb(grb_id, GCN_NAME="'%s'" % packet.candidateName())
        insertGcnNotice(grb_id, packet.buffer, current_date(), packet.MET)
        return grb_id
    def run(self):
        self._listen()
        last_imalive = 0
        try:
            while True:
                newSocket, address = self.sock.accept()
                print "Connected from", address
                newSocket.setblocking(0)
                while True:
                    inp, outp, exc = select.select([newSocket], [], [], 15)
                    if len(inp) == 0:
                        print "Timeout waiting for data.  Reopening socket."
                        break
                    receivedData = newSocket.recv(self.bufsize)
                    packet = GcnPacket(receivedData)
                    if packet.type == self._KILL_SOCKET:
                        print "KILL_SOCKET packet received.  Reopening socket."
                        break
                    newSocket.send(receivedData)
                    if packet.type == self._IM_ALIVE:
                        dt = packet.arrTime - last_imalive
                        print "IM_ALIVE packet received at", packet.arrTime
                        if last_imalive and not 8 < dt < 12:
                            print "Time between last two packets: %i" % dt
                        last_imalive = packet.arrTime
                    else:
                        emailNotice(packet, self.recipients)
                        # Instead of creating a text version of the Notice
                        # this should instead create an entry in the GRB
                        # database table and then launch the refinement
                        # task.
                        grb_id = self.registerWithDatabase(packet)
                        notice_file = noticeGenerator(packet)
                        refinementStreams(notice_file, _outputDir, debug=True)
                        print "Packet of type %i received" % packet.type
                newSocket.close()
        except socket.error, message:
            print "socket error:", message[1]
        except Exception, message:
            print "Other exception raised: ", message
        print "Closing server socket to", address
        self.sock.close()

if __name__ == '__main__':
    gcnServer = GcnServer(port=5264)
#    gcnServer = GcnServer()
    while True:
        gcnServer.run()
        print "reopening connection..."
