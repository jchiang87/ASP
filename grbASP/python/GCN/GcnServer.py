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

def emailNotice(packet, address="jchiang@slac.stanford.edu"):
    import smtplib
    packet_type = "GCN Packet type %i" % packet.type
    subj = packet_type
    fromadr = address
    hdr = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromadr, address, subj)
    message = "%s%s" % (hdr, packet)
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    mail.sendmail(fromadr, address, message)
    mail.quit()

class Packet(object):
    _items = ('type', 'serialNum', 'hopCount', 'packetSOD', 'triggerNum',
              'TJD', 'SOD', 'RA', 'Dec', 'intensity', 'peakIntensity',
              'posError', 'SC_Az', 'SC_El', 'SC_x_RA', 'SC_x_Dec',
              'SC_z_RA', 'SC_z_Dec', 'trigger_id', 'misc',
              'Earth_SC_Az', 'Earth_SC_El', 'SC_radius', 't_peak')
    _floats = ('packetSOD', 'SOD', 'RA', 'Dec', 'SC_Az', 'SC_El',
               'SC_x_RA', 'SC_x_Dec', 'SC_z_RA', 'SC_z_Dec', 't_peak')
    def __init__(self, buffer):
        self.arrTime = time.time()
        self.buffer = array.array('l', buffer)
        self.buffer.byteswap()
        # just process the most common items for now
        for i, item in enumerate(self._items[:9]):
            self.__dict__[item] = self.buffer[i]
        for item in self._floats[:4]:
            self.__dict__[item] /= 100.
        # RA and Dec have an additional factor of 100 scaling for the
        # Notices we receive (i.e., from Integral and Swift)
        self.__dict__['RA'] /= 100.
        self.__dict__['Dec'] /= 100.
    def __repr__(self):
        summary = ""
        for item in self._items[:9]:
            summary += "%s : %s\n" % (item, self.__dict__[item])
        return summary

class GcnServer(object):
    _IM_ALIVE = 3
    _KILL_SOCKET = 4
    def __init__(self, port=5263, bufsize=4*40):
        self.port = port
        self.bufsize = bufsize
    def _listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", self.port))
        self.sock.listen(5)
#        self.oldexitfunc = getattr(sys, 'exitfunc', None)
#        sys.exitfunc = self.cleanup
    def cleanup(self):
        print "Program exit"
        self.sock.close()
        try: 
            self.oldexitfunc(self)
        except: 
            pass
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
                    packet = Packet(receivedData)
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
                        emailNotice(packet)
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
