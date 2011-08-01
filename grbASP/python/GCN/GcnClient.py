"""
@brief Toy simulator for GCN packet sender.  This acts like the GCN client
at Goddard.

@author P. Nolan <Patrick.Nolan@stanford.edu>
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import sys
import glob
import socket
import array
import time

def simple_packet(type):
    my_packet = array.array("l", (type,) + 39*(0,))
    if my_packet.itemsize == 8:
        # Force 4 byte array if on 64 bit machine
        my_packet = array.array("i", (type,) + 39*(0,))
    my_packet.byteswap()
    return my_packet

im_alive = simple_packet(3)
kill_socket = simple_packet(4)

_items = ['type', 'serialNum', 'hopCount', 'packetSOD', 'triggerNum',
          'TJD', 'SOD', 'RA', 'Dec', 'intensity', 'peakIntensity',
          'posError', 'SC_Az', 'SC_El', 'SC_x_RA', 'SC_x_Dec',
          'SC_z_RA', 'SC_z_Dec', 'trigger_id', 'misc',
          'Earth_SC_Az', 'Earth_SC_El', 'SC_radius', 't_peak']

def build_packet(infile):
    buffer = array.array("l", 40*(0,))
    if buffer.itemsize == 8:
        buffer = array.array("i", 40*(0,))
    for line in open(infile):
        data = line.split('=')
        buffer[_items.index(data[0].strip())] = int(data[1].strip())
    buffer.byteswap()
    return buffer

class GcnClient(object):
    def __init__(self, hostname="localhost", port=5264):
        self.hostname, self.port = hostname, port
    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.hostname, self.port))
    def run(self):
        try:
            self._connect()
            while True:
                self.send(im_alive)
        except socket.error, message:
            print message[1]
            self.sock.close()
    def _send_packets(self):
        files = glob.glob('*.dat')
        for item in files:
            self.send(build_packet(item), 0)
            os.rename(item, item + '_sent')
    def send(self, packet, dt=10):
        print self.sock.send(packet)
        self.sleep(dt)
    def sleep(self, dt):
        for i in range(dt, 0, -1):
            sys.stdout.write("%3i" % i)
            sys.stdout.flush()
            sys.stdout.write("\r")
            time.sleep(1)
            self._send_packets()

if __name__ == '__main__':
    client = GcnClient()
    client.run()
