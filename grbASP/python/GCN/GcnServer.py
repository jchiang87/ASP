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

class Packet(object):
    _items = ('type', 'serialNum', 'hopCount', 'packetSOD', 'triggerNum',
              'TJD', 'SOD', 'RA', 'Dec', 'intensity', 'peakIntensity',
              'posError', 'SC_Az', 'SC_El', 'SC_x_RA', 'SC_x_Dec',
              'SC_z_RA', 'SC_z_Dec', 'trigger_id', 'misc',
              'Earth_SC_Az', 'Earth_SC_El', 'SC_radius', 't_peak')
    _floats = ('packetSOD', 'SOD', 'RA', 'Dec', 'SC_Az', 'SC_El',
               'SC_x_RA', 'SC_x_Dec', 'SC_z_RA', 'SC_z_Dec', 't_peak')
    _JD_missionStart_seconds = 211845067200
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
        self.MET = ((self.TJD + 2440000.5)*8.64e4 + self.SOD 
                    - self._JD_missionStart_seconds)
    def __repr__(self):
        summary = ""
        for item in self._items[:9]:
            summary += "%s : %s\n" % (item, self.__dict__[item])
        return summary

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
                        emailNotice(packet, self.recipients)
                        # instead of creating a text version of the Notice
                        # this should instead create an entry in the GRB
                        # database table and then launch the refinement
                        # task.
                        notice_file = noticeGenerator(packet)
                        refinementStreams(notice_file, _outputDir)
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
