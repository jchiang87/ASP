"""
@brief Writer for packet text files that are sent by the mock
GcnClient.  This script allows the client to set the RA, Dec of the
burst and the burst time in MET, converting the latter to TJD/SOD
pairs. These data are packed into the 40x4byte word byte-swapped
packet format that GCN uses by the GcnClient.py code.

@author J. Chiang
"""
#
# $Header$
#

import sys

_keys = ('type', 'serialNum', 'hopCount', 'packetSOD', 'triggerNum',
         'TJD', 'SOD', 'RA', 'Dec', 'intensity', 'peakIntensity',
         'posError', 'SC_Az', 'SC_El', 'SC_x_RA', 'SC_x_Dec',
         'SC_z_RA', 'SC_z_Dec', 'trigger_id', 'misc',
         'Earth_SC_Az', 'Earth_SC_El', 'SC_radius', 't_peak')
_JD_missionStart_seconds = 211845067200

class PacketFile(dict):
    def __init__(self):
        [self.__setitem__(key, 0) for key in _keys]
        self['type'] = 9
        self['serialNum'] = 100001
        self['hopCount'] = 1
    def setCoord(self, ra, dec):
        self['RA'] = int(ra*1e4)
        self['Dec'] = int(dec*1e4)
    def setTriggerNum(self, triggerNum):
        self['triggerNum'] = triggerNum
    def setBurstTime(self, MET):
        jd = (MET + _JD_missionStart_seconds)/8.64e4
        tjd = jd - 2440000.5
        sod = (tjd % 1)*8.64e4
        self['SOD'] = int(sod*100)
        self['TJD'] = int(tjd)
    def write(self, outfile):
        output = open(outfile, 'w')
        for item in self.keys():
            output.write('%s = %i\n' % (item, self[item]))
        output.close()

if __name__ == '__main__':
    foo = PacketFile()
    foo.setCoord(269.959, -29.084)
    foo.setBurstTime(252659970)
    foo.write('my_packet.dat')
    
