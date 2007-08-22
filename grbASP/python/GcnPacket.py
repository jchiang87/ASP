"""
@brief GCN Packet interface.  Input is a raw 160 byte buffer, such as those
       obtained directly from GCN.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import time
import array
import pyASP

class GcnPacket(object):
    _items = ('type', 'serialNum', 'hopCount', 'packetSOD', 'triggerNum',
              'TJD', 'SOD', 'RA', 'Dec', 'intensity', 'peakIntensity',
              'posError', 'SC_Az', 'SC_El', 'SC_x_RA', 'SC_x_Dec',
              'SC_z_RA', 'SC_z_Dec', 'trigger_id', 'misc',
              'Earth_SC_Az', 'Earth_SC_El', 'SC_radius', 't_peak')
    _floats = ('packetSOD', 'SOD', 'RA', 'Dec', 'posError', 'SC_Az', 'SC_El',
               'SC_x_RA', 'SC_x_Dec', 'SC_z_RA', 'SC_z_Dec', 't_peak')
    _JD_missionStart_seconds = 211845067200
    def __init__(self, buffer):
        self.arrTime = time.time()
        self.buffer = array.array('l', buffer)
        self.buffer.byteswap()
        # just process the most common items for now, i.e., from 'type'
        # to 'posErr'
        for i, item in enumerate(self._items[:12]):
            self.__dict__[item] = self.buffer[i]
        for item in self._floats[:5]:
            self.__dict__[item] /= 100.
        # RA, Dec, and posError have an additional factor of 100
        # scaling for the Notices we receive (i.e., from Integral and
        # Swift)
        self.__dict__['RA'] /= 100.
        self.__dict__['Dec'] /= 100.
        self.__dict__['posError'] /= 100.
        self.MET = ((self.TJD + 2440000.5)*8.64e4 + self.SOD 
                    - self._JD_missionStart_seconds)
        self.buffer.byteswap()   # restore buffer
    def candidateName(self):
        tjd = self.TJD
        sod = self.SOD
        jd = pyASP.JulianDate(tjd + 2440000.5 + sod/8.64e4)
        self.start_time = (jd.seconds() -
                           pyASP.JulianDate_missionStart().seconds())
        year, month, day, hours = jd.gregorianDate()
        return 'GRB%02i%02i%02i%03i' % (year % 100, month, day, hours/24.*1000)
    def __repr__(self):
        summary = ""
        for item in self._items[:9]:
            summary += "%s : %s\n" % (item, self.__dict__[item])
        return summary

if __name__ == '__main__':
    buffer = array.array('l', 40*(0,))
    buffer[5] = 14469       # TJD for GRB080104514
    buffer[6] = 4443296     # SOD
    buffer.byteswap()
    packet = GcnPacket(buffer.tostring())
    print packet.candidateName()
