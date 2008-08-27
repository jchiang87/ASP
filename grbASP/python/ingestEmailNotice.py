"""
@brief Script to ingest incoming GCN Notices and fill the data in the
ASP GCNNOTICES database.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import string
import array
import dbAccess
import pyASP
import datetime

def round(x):
    frac = x % 1
    if frac > 0.5:
        return int(x) + 1
    return int(x)

_GCN_Notice_types = {"MILAGRO_POSITION" : 58,
                     "SWIFT_BAT_POSITION" : 61,
                     "SWIFT_SC_SLEW" : 66,
                     "SWIFT_XRT_POSITION" : 67,
                     "SWIFT_XRT_POSITION_NACK" : 71}

_months = {}
for i, item in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
    _months[item] = i + 1

class Packet(object):
    _JD_missionStart_seconds = 211845067200
    def __init__(self, infile):
        self._parseEmailNotice(infile)
        self.MET = self._MET()
        self.Name = self.candidateName()
        self._build_packet()
    def _parseEmailNotice(self, infile):
        self.notice_type = "None"
        self.notice_date = datetime.datetime.utcnow()
        for line in open(infile):
            if line.find('GRB_RA:') == 0:
                self.RA = float(line.split()[1].strip('d'))
            elif line.find('GRB_DEC:') == 0:
                self.Dec = float(line.split()[1].strip('d'))
            elif line.find('Subject: GCN') == 0:
                self.notice_type = line.split()[1].split('/')[-1]
                self.mission = self.notice_type.split('_')[0]
            elif line.find('GRB_ERROR:') == 0:
                self.posError = float(line.split()[1])
                #
                # Convert to degrees, if necessary
                #
                if line.find('arcmin') > 0:
                    self.posError /= 60. 
                elif line.find('arcsec') > 0:
                    self.posError /= (60.*60.)
            elif (line.find('GRB_DATE:') == 0 or 
                  line.find('IMG_START_DATE') == 0):
                self.TJD = int(line.split()[1])
            elif (line.find('GRB_TIME:') == 0 or 
                  line.find('IMG_START_TIME') == 0):
                self.SOD = int(float(line.split()[1]))
            elif line.find('NOTICE_DATE') == 0:
                self._parseNoticeDate(line)
            elif line.find("TRIGGER_NUM:") == 0:
                # This line combines the trigger number and
                # sequence/segment number and does not have canonical
                # form, so we have this ugly parsing code:
                trig_value = line[12:].split()[0].split(',')[0]
                self.trigger_num = int(trig_value)
    def _parseNoticeDate(self, line):
        tokens = line.split('DATE:')[-1].strip().split()
        day = int(tokens[1])
        month = _months[tokens[2]]
        year = 2000 + int(tokens[3])
        hh, mm, ss = tokens[4].split(':')
        hours = int(hh)
        mins = int(mm)
        secs = int(ss)
        self.notice_date = datetime.datetime(year, month, day, 
                                             hours, mins, secs)
    def _build_packet(self):
        self.buffer = array.array("l", 40*(0,))
        self.buffer[7] = int(self.RA*1e4)
        self.buffer[8] = int(self.Dec*1e4)
        try:
            self.buffer[11] = int(self.posError*1e4)
        except AttributeError:
            pass
        self.buffer[5] = self.TJD
        self.buffer[6] = self.SOD*100
        self.buffer.byteswap()
    def candidateName(self):
        tjd = self.TJD
        sod = self.SOD
        jd = pyASP.JulianDate(tjd + 2440000.5 + sod/8.64e4)
        # Add a leap second for the one added Dec 31, 2005.
        # Another will be needed after Dec 31, 2008.
        self.start_time = (jd.seconds() -
                           pyASP.JulianDate_missionStart().seconds() + 1)
        year, month, day, hours = jd.gregorianDate()
#        return 'GRB%02i%02i%02i%03i' % (year % 100, month, day, hours/24.*1000)
        return 'GRB%02i%02i%02i%03i' % (year % 100, month, day, 
                                        round(sod/86400.*1000))
    def _MET(self):
        # Add a leap second for the one added Dec 31, 2005.
        # Another will be needed after Dec 31, 2008.
        return int((self.TJD + 2440000.5)*8.64e4 + self.SOD
                   - self._JD_missionStart_seconds + 1)
        
def registerWithDatabase(packet, notice_file):
    grb_id = int(packet.MET)
    triggerTimes = dbAccess.gcnTriggerTimes(packet.mission, packet.trigger_num)
    if not dbAccess.haveGrb(grb_id) and not triggerTimes:
        dbAccess.insertGrb(grb_id)
        dbAccess.updateGrb(grb_id, GCN_NAME="'%s'" % packet.Name,
                           INITIAL_LAT_RA=packet.RA, 
                           INITIAL_LAT_DEC=packet.Dec,
                           INITIAL_ERROR_RADIUS=packet.posError, 
                           GCN_NOTICE_FILE="'%s'" % notice_file,
                           ASP_PROCESSING_LEVEL=0)
        isUpdate = 0
    else:
        grb_id = triggerTimes[0][0]
        isUpdate = 1

    dbAccess.insertGcnNotice(grb_id, packet.buffer, packet.mission,
                             packet.trigger_num, packet.notice_date,
                             packet.MET, packet.RA, packet.Dec,
                             packet.posError, isUpdate=isUpdate,
                             notice_type=packet.notice_type)
    return grb_id

if __name__ == '__main__':
    import sys
    import glob

    packet = Packet(sys.argv[1])
    registerWithDatabase(packet, '/foo')
    print packet.MET, packet.Name
