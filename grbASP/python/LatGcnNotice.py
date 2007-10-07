"""
@brief Encapsulation of a LAT GCN Notice.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import copy
import time
import array
import celgal
import pyASP
import dbAccess

_dataDir = os.path.join(os.environ['GRBASPROOT'], 'data')

class ConvertEpoch(object):
    def __init__(self):
        self._j2000 = celgal.celgal(J2000=1)
        self._b1950 = celgal.celgal(J2000=0)
    def J2000(self, ra, dec):
        l, b = self._b1950.gal((ra, dec))
        return self._j2000.cel((l, b))
    def B1950(self, ra, dec):
        l, b = self._j2000.gal((ra, dec))
        return self._b1950.cel((l, b))

class LatGcnTemplate(dict):
    def __init__(self, template=os.path.join(_dataDir, 'GCN_Notice.tpl')):
        self.ordered_keys = []
        for line in open(template):
            if line.find('COMMENTS') == 0:
                break
            if line.find(':') > 0:
                data = line.split(':')
                key, value = data[0], (':'.join(data[1:])).strip()
                self.ordered_keys.append(key)
            else:
                value += '\n' + line.strip('\n')
            self[key] = value
    def __repr__(self):
        lines = []
        for key in self.ordered_keys:
            lines.append("%-16s%s" % (key + ":", self[key]))
        return '\n'.join(lines)

def sexigesimal(ra, dec):
    degperhr = 360/24
    ra_hours = int(ra/degperhr)
    ra_mins = int((ra - ra_hours*degperhr)/degperhr*60.)
    ra_secs = int((ra - ra_hours*degperhr -ra_mins/60.*degperhr)/degperhr*3600)

    sign = 1
    if dec < 0:
        sign = -1
        dec *= -1
        
    dec_degs = int(dec)
    dec_mins = int((dec - dec_degs)*60)
    frac = dec - dec_degs - dec_mins/60.
    dec_secs = int(frac*3600)
    if sign == 1:
        return ("+%02ih %02im %02is" % (ra_hours, ra_mins, ra_secs),
                "+%02id %02i' %02i\"" % (dec_degs, dec_mins, dec_secs))
    else:
        return ("+%02ih %02im %02is" % (ra_hours, ra_mins, ra_secs),
                "-%02id %02i' %02i\"" % (dec_degs, dec_mins, dec_secs))
 
def dec_string(dec, sexiges):
    if dec >= 0:
        return '+%6.3fd {%s}' % (dec, sexiges)
    else:
        return '%7.3fd {%s}' % (dec, sexiges)

def time_string(secOfDay):
    hours = int(secOfDay/3600.)
    mins = int((secOfDay - hours*3600)/60.)
    secs = secOfDay - hours*3600 - mins*60.
    return ("%.2f SOD {%02i:%02i:%02i.%02i} UT (trigger time)"
            % (secOfDay, hours, mins, int(secs), secs % 1))

class LatGcnNotice(object):
    def __init__(self, burstTime, ra, dec):
        self.notice = LatGcnTemplate()
        self.notice['NOTICE_DATE'] = time.asctime()
        self._packet = array.array("l", 40*(0,))
        self.met = burstTime
        self.grb_id = int(self.met)
        self.ra = ra
        self.dec = dec
        self._setTime(burstTime)
        self._setCoords(ra, dec)
    def setLocErr(self, error):
        self.notice['GRB_ERROR'] = ('%.2f [arcmin radius, statistical only]'
                                    % (error*60))
    def setIntens(self, counts):
        foo = self.notice
        foo['GRB_INTEN1'] = '%i [0.0 < cnts < 0.1 (GeV)]' % counts[0]
        foo['GRB_INTEN2'] = '%i [0.1 < cnts < 1.0 (GeV)]' % counts[1]
        foo['GRB_INTEN3'] = '%i [1.0 < cnts < 10. (GeV)]' % counts[2]
        foo['GRB_INTEN4'] = '%i [10. < cnts (GeV)]' % counts[3]
    def setTriggerNum(self, triggerNum):
        self.notice['TRIGGER_NUM'] = '%i,   Sequence_Num: 0' % triggerNum
        self._packet[4] = int(triggerNum)
    def setDuration(self, duration):
        foo = self.notice
        foo['TRIGGER_DUR'] = ('%.3f [sec] (interval, Tlast-Tfirst photons)'
                              % duration)
    def addComment(self, comment):
        self.notice['COMMENT'] = `comment`
    def _setCoords(self, ra, dec):
        converter = ConvertEpoch()
        b1950 = converter.B1950(ra, dec)
        ra2000, dec2000 = sexigesimal(ra, dec)
        ra1950, dec1950 = sexigesimal(*b1950)
        foo = self.notice
        foo['GRB_RA'] = ('%7.3fd {%s} (J2000),\n%16s%7.3fd {%s} (B1950)'
                         % (ra, ra2000, ' ', b1950[0], ra1950))
        foo['GRB_DEC'] = ('%s (J2000),\n%16s%s (B1950)'
                          % (dec_string(dec, dec2000), ' ',
                             dec_string(b1950[1], dec1950)))
        self._packet[7] = int(self.ra*1e4)
        self._packet[8] = int(self.dec*1e4)
    def _setTime(self, burstTime):
        jd = pyASP.jd_from_MET(burstTime)
        year, month, day, hours = jd.gregorianDate()
        foo = self.notice
        foo['GRB_DATE'] = ('%i TJD; %i DOY; %s/%s/%s' %
                           (jd.tjd(), jd.dayOfYear(), year%100, month, day))
        foo['GRB_TIME'] = time_string(hours*3600)
        self.name = ('GRB%02i%02i%02i%03i' %
                     (year % 100, month, day, hours/24.*1000))
        JD_missionStart_seconds = 211845067200
        jd = (self.met + JD_missionStart_seconds)/8.64e4
        tjd = jd - 2440000.5
        sod = (tjd % 1)*8.64e4
        self._packet[5] = int(tjd)
        self._packet[6] = int(sod*100)
    def write(self, outfile):
        output = open(outfile, 'w')
        output.write(str(self.notice))
        output.close()
    def GcnPacket(self):
        packet = copy.copy(self._packet)
        packet.byteswap()
        return packet
    def registerWithDatabase(self, grb_id=None, isUpdate=False):
        if grb_id is None:
            grb_id = self.grb_id
        try:
            dbAccess.insertGrb(grb_id)
        except dbAccess.cx_Oracle.DatabaseError, message:
            # GRB_ID is already in GRB table
            print message
            pass
        # need to implement error radius estimate
        dbAccess.updateGrb(grb_id, GCN_NAME="'%s'" % self.name,
                           INITIAL_RA=self.ra, INITIAL_DEC=self.dec,
                           INITIAL_ERROR_RADIUS=1, ANALYSIS_VERSION=0,
                           L1_DATA_AVAILABLE=0)
        dbAccess.insertGcnNotice(grb_id, self.GcnPacket(), 
                                 dbAccess.current_date(), self.met, 
                                 self.ra, self.dec, 1, isUpdate=int(isUpdate))

if __name__ == '__main__':
    notice = LatGcnNotice(222535575.0, 305.723, -67.0446)
    notice.setLocErr(0.33)
    notice.setIntens((20, 5, 0, 1))
    notice.setDuration(12.33)
    notice.write('foo.txt')
