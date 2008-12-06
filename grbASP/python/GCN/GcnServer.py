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

from createGrbStreams import refinementStreams
from GcnPacket import GcnPacket
import dbAccess
from LatGcnNotice import LatGcnNotice

def _outputDir(grb_id):
    dirname = os.path.join(os.environ['OUTPUTDIR'], '%i' % grb_id)
    try:
        os.mkdir(dirname)
        os.chmod(dirname, 0777)
    except OSError:
        if os.path.isdir(dirname):
            os.chmod(dirname, 0777)
        else:
            raise OSError, "Error creating directory: " + dirname
    return dirname

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
        outfile = os.path.join(_outputDir(packet.MET), 
                               "GRB%i_Notice.txt" % packet.MET)
    my_notice = LatGcnNotice(packet.MET, packet.RA, packet.Dec)
    my_notice.setTriggerNum(packet.triggerNum)
    my_notice.write(outfile)
    return outfile

class GcnServer(object):
    _IM_ALIVE = 3
    _KILL_SOCKET = 4
    def __init__(self, port=5263, bufsize=4*40, dt_alive=60):
        self.port = port
        self.bufsize = bufsize
        self.recipients = ["jchiang@slac.stanford.edu"]
        self.dt_alive = dt_alive
    def _listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", self.port))
        self.sock.listen(5)
    def registerWithDatabase(self, packet):
        grb_id = int(packet.MET)
        try:
            dbAccess.insertGrb(grb_id)
        except dbAccess.cx_Oracle.DatabaseError, message:
            print message
            pass
        dbAccess.updateGrb(grb_id, GCN_NAME="'%s'" % packet.candidateName(),
                           INITIAL_RA=packet.RA, INITIAL_DEC=packet.Dec,
                           INITIAL_ERROR_RADIUS=packet.posError)
        dbAccess.insertGcnNotice(grb_id, packet.buffer, 
                                 dbAccess.current_date(), packet.MET)
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
                    inp, outp, exc = select.select([newSocket], [], [], 
                                                   3*self.dt_alive)
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
                        if (last_imalive and 
                            not self.dt_alive - 2 < dt < self.dt_alive + 2):
                            print "Time between last two packets: %i" % dt
                        last_imalive = packet.arrTime
                    else:
                        emailNotice(packet, self.recipients)
                        notice_file = noticeGenerator(packet)
                        grb_id = self.registerWithDatabase(packet)
                        refinementStreams((grb_id,), _outputDir(grb_id))
                        print "Packet of type %i received" % packet.type
                newSocket.close()
        except socket.error, message:
            print "socket error:", message[1]
        except Exception, message:
            print "Other exception raised: ", message
        print "Closing server socket to", address
        self.sock.close()

if __name__ == '__main__':
    gcnServer = GcnServer(port=5264, dt_alive=10)
#    gcnServer = GcnServer()
    while True:
        gcnServer.run()
        print "reopening connection..."
