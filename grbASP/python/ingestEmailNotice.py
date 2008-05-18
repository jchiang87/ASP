"""
@brief Script to ingest incoming GCN Notices and fill the data in the
ASP GCNNOTICES database.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import array
import dbAccess
import pyASP
import datetime

class Packet(object):
    _JD_missionStart_seconds = 211845067200
    def __init__(self, RA, Dec, posError, TJD, SOD, MET=None, Name=None,
                 notice_type=None, notice_date=None):
        (self.RA, self.Dec, self.posError, self.TJD,
         self.SOD, self.MET, self.Name)= (RA, Dec, posError, TJD, SOD, 
                                          MET, Name)
        self.notice_type = notice_type
        self.notice_date = notice_date
        if self.MET is None:
            self.MET = self._MET()
        if self.Name is None:
            self.Name = self.candidateName()
        if self.notice_type is None:
            self.notice_type = "None"
        if self.notice_date is None:
            self.notice_date = datetime.datetime.utcnow()
        self._build_packet()
    def _build_packet(self):
        self.buffer = array.array("l", 40*(0,))
        self.buffer[7] = int(self.RA*1e4)
        self.buffer[8] = int(self.Dec*1e4)
        self.buffer[11] = int(self.posError*1e4)
        self.buffer[5] = self.TJD
        self.buffer[6] = self.SOD*100
        self.buffer.byteswap()
    def candidateName(self):
        tjd = self.TJD
        sod = self.SOD
        jd = pyASP.JulianDate(tjd + 2440000.5 + sod/8.64e4)
        self.start_time = (jd.seconds() -
                           pyASP.JulianDate_missionStart().seconds())
        year, month, day, hours = jd.gregorianDate()
        return 'GRB%02i%02i%02i%03i' % (year % 100, month, day, hours/24.*1000)
    def _MET(self):
        return int((self.TJD + 2440000.5)*8.64e4 + self.SOD
                   - self._JD_missionStart_seconds)
        
def registerWithDatabase(packet):
    grb_id = int(packet.MET)
    if not dbAccess.haveGrb(grb_id):
        dbAccess.insertGrb(grb_id)
        dbAccess.updateGrb(grb_id, GCN_NAME="'%s'" % packet.Name,
                           INITIAL_LAT_RA=packet.RA, 
                           INITIAL_LAT_DEC=packet.Dec,
                           INITIAL_ERROR_RADIUS=packet.posError, 
                           ASP_PROCESSING_LEVEL=0)
        isUpdate = 0
    else:
        isUpdate = 1

    dbAccess.insertGcnNotice(grb_id, packet.buffer, 
                             packet.notice_date,
                             packet.MET, packet.RA, packet.Dec,
                             packet.posError, isUpdate=isUpdate,
                             notice_type=packet.notice_type)
    return grb_id

_GCN_Notice_types = {"MILAGRO_POSITION" : 58,
                     "SWIFT_BAT_POSITION" : 61,
                     "SWIFT_SC_SLEW" : 66,
                     "SWIFT_XRT_POSITION" : 67,
                     "SWIFT_XRT_POSITION_NACK" : 71}

months = {}
for i, item in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
    months[item] = i + 1

def parseNoticeDate(line):
    tokens = line.split('DATE:')[-1].strip().split()
    day = int(tokens[1])
    month = months[tokens[2]]
    year = 2000 + int(tokens[3])
    hh, mm, ss = tokens[4].split(':')
    hours = int(hh)
    mins = int(mm)
    secs = int(ss)
    return datetime.datetime(year, month, day, hours, mins, secs)

def parseEmailNotice(infile):
    notice_type = None
    for line in open(infile):
        if line.find('GRB_RA:') == 0:
            ra = float(line.split()[1].strip('d'))
        elif line.find('GRB_DEC:') == 0:
            dec = float(line.split()[1].strip('d'))
        elif line.find('GRB_ERROR:') == 0:
            posError = float(line.split()[1])/60. # convert from arcmin to deg
        elif line.find('GRB_DATE:') == 0:
            TJD = int(line.split()[1])
        elif line.find('GRB_TIME:') == 0:
            SOD = int(line.split()[1])
        elif line.find('NOTICE_DATE') == 0:
            notice_date = parseNoticeDate(line)
        elif line.find('Subject:') == 0:
            notice_type = line.split()[1].split('/')[-1]
    return ra, dec, posError, TJD, SOD, None, None, notice_type, notice_date

if __name__ == '__main__':
    import sys
    import glob

    infile = sys.argv[1]

    packet = Packet(*parseEmailNotice(infile))
    registerWithDatabase(packet)
    print packet.MET, packet.Name
