"""
@brief Encapsulation of a LAT GCN Notice.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import copy
import string
import datetime
import array
import celgal
import pyASP
import dbAccess
import numpy as num
from FitsNTuple import FitsNTuple, FitsNTupleError
from MultiPartMailer import MultiPartMailer

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
            if line.find("#") == 0:   # skip this line
                continue
#            if line.find('COMMENTS') == 0:
#                continue
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
        return '%6.3fd {%s}' % (dec, sexiges)
    else:
        return '%7.3fd {%s}' % (dec, sexiges)

def time_string(secOfDay):
    hours = int(secOfDay/3600.)
    mins = int((secOfDay - hours*3600)/60.)
    secs = secOfDay - hours*3600 - mins*60.
    return ("%.2f SOD {%02i:%02i:%02i.%02i} UT (trigger time)"
            % (secOfDay, hours, mins, int(secs), secs % 1))

months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

def notice_date():
    "Return current date string using GCN Notice formatting"
    utcnow = datetime.datetime.utcnow()
    my_date = ("%3s %02i %3s %02i %02i:%02i:%02i UT" %
               (weekdays[utcnow.weekday()], utcnow.day, months[utcnow.month-1],
                utcnow.year % 2000, utcnow.hour, utcnow.minute, utcnow.second))
    return my_date

def utc_date(met):
    missionStart = datetime.datetime(2001, 1, 1, 0, 0, 0)
    dt = datetime.timedelta(0, met)
    utc = missionStart + dt
    my_date = ("%3s %02i %3s %02i %02i:%02i:%02i UT" %
               (weekdays[utc.weekday()], utc.day, months[utc.month-1],
                utc.year % 2000, utc.hour, utc.minute, utc.second))
    return my_date

class LatGcnNotice(object):
    def __init__(self, burstTime, ra, dec):
        self.notice = LatGcnTemplate()
        self.notice['NOTICE_DATE'] = notice_date()
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
        self._packet[11] = error*100
    def setIntens(self, counts):
        foo = self.notice
        foo['GRB_INTEN1'] = '%i [0.0 < cnts < 0.1 (GeV)]' % counts[0]
        foo['GRB_INTEN2'] = '%i [0.1 < cnts < 1.0 (GeV)]' % counts[1]
        foo['GRB_INTEN3'] = '%i [1.0 < cnts < 10. (GeV)]' % counts[2]
        foo['GRB_INTEN4'] = '%i [10. < cnts (GeV)]' % counts[3]
    def setTriggerNum(self, triggerNum):
        self.notice['TRIGGER_NUM'] = '%i' % triggerNum
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
        foo['GRB_RA'] = '%7.3fd {%s} (J2000)' % (ra, ra2000)
        foo['GRB_DEC'] = '%s (J2000)' % dec_string(dec, dec2000)
        self._packet[7] = int(self.ra*1e4)
        self._packet[8] = int(self.dec*1e4)
    def _setTime(self, burstTime):
        jd = pyASP.jd_from_MET(burstTime)
        year, month, day, hours = jd.gregorianDate()
        foo = self.notice
#        foo['GRB_DATE'] = ('%i TJD; %i DOY; %2i/%2i/%2i' %
#                           (jd.tjd(), jd.dayOfYear(),
#                            int(year%100), int(month), int(day)))
        foo['GRB_DATE'] = ('%i TJD; %i DOY' % (jd.tjd(), jd.dayOfYear()))
        foo['GRB_TIME'] = time_string(hours*3600)
        
        grb_name = 'GRB%02i%02i%02i%03i' % (year % 100, month, day, 
                                            1000*hours/24.)
        self.name = grb_name
        
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
                           INITIAL_LAT_RA=self.ra, INITIAL_LAT_DEC=self.dec,
                           INITIAL_ERROR_RADIUS=1, ASP_PROCESSING_LEVEL=0)
        dbAccess.insertGcnNotice(grb_id, self.GcnPacket(), "GLAST", grb_id,
                                 datetime.datetime.utcnow(), self.met, 
                                 self.ra, self.dec, 1, isUpdate=int(isUpdate),
                                 notice_type="ASP_BLIND_SEARCH")
    def email_notification(self, logProbValue, threshold, 
                           recipients=None, files=None, figures=()):
        if recipients is None:
#            recipients = dbAccess.grbAdvocateEmails()
            recipients = ['balist@glast.stanford.edu',
                          'jchiang@slac.stanford.edu']
        print recipients

        mailer = MultiPartMailer("ASP blind search GRB candidate",
                                 "solist@glast.stanford.edu")
        message = ("ASP GRB_blind_search found a burst candidate at\n\n" +
                   "  (RA, Dec) = (%.3f, %.3f)\n\n" % (self.ra, self.dec) +
                   "with trigger time\n\n"
                   "  %s\n  MET = %.3f\n\n" % (utc_date(self.met), self.met) + 
                   "and log-probability / threshold : " + 
                   "  %.1f / %.1f \n" % (logProbValue, threshold) +
                   "Plots of log-probabilty distributions are attached.\n")
        if files is not None:
            message += "\nFiles used:\n"
            for item in files:
                message += (item + "\n")
        message += "\nhttp://glast-ground.slac.stanford.edu/ASPDataViewer/\n"
        mailer.add_text(message)
        for item in figures:
            mailer.add_image(item)
        mailer.finish()
        mailer.send('glastgcn@slac.stanford.edu', recipients)
def latCounts(ft1File):
    ebounds = (1e2, 1e3, 1e4)
    try:
        ft1 = FitsNTuple(ft1File)
    except FitsNTupleError:
        return 0, 0, 0, 0
    foo = []
    for ee in ebounds:
        indx = num.where(ft1.ENERGY < ee)
        foo.append(len(indx[0]))
    foo.append(len(ft1.ENERGY))
    return (foo[0], foo[1] - foo[0], foo[2] - foo[1], foo[3] - foo[2])

if __name__ == '__main__':
    import glob
    from parfile_parser import Parfile
    from pyASP import SkyDir
    from ScData import ScData

    output_dir = os.environ['OUTPUTDIR']

    os.chdir(output_dir)
    grb_id = int(os.environ['GRB_ID'])

    sql = "select TS_VALUE from GRB where GRB_ID=%i and GCAT_FLAG=0" % grb_id
    def getTs(cursor):
        for entry in cursor:
            return entry[0]
    Ts_value = dbAccess.apply(sql, getTs)

    if Ts_value is not None and Ts_value < 25:
        print "Likely non-detection in Level-1 data. TS = ", Ts_value

    pars = Parfile(glob.glob('*_pars.txt')[0])

    notice = LatGcnNotice(pars['tstart'], pars['ra'], pars['dec'])

    notice.setLocErr(pars['loc_err'])

    notice.setIntens(latCounts(pars['name'] + '_LAT_3.fits'))

    notice.setTriggerNum(grb_id)

    notice.setDuration(pars['tstop'] - pars['tstart'])

    notice.notice['SIGNIFICANCE'] = '%.1f [sqrt(TS) 2 dof]' % num.sqrt(Ts_value)

    notice.notice['GRB_INTEN1'] = ("%.1f [0.1 < cnts < 1.0 (GeV)]"
                                   % pars['GRB_INTEN1'])
    notice.notice['GRB_INTEN2'] = ("%.1f [1.0 < cnts < 10. (GeV)]"
                                   % pars['GRB_INTEN2'])
    notice.notice['GRB_INTEN3'] = ("%.1f [10. < cnts (GeV)]" 
                                   % pars['GRB_INTEN3'])
                                   
    ft2File = open(pars['name'] + '_files').readlines()[-1].strip()
    scData = ScData(ft2File)
    srcDir = SkyDir(pars['ra'], pars['dec'])
    notice.notice['GRB_THETA'] = ("%.2f [deg]" % 
                                  scData.inclination(pars['tstart'], srcDir))
    notice.notice['GRB_PHI'] = ("%.2f [deg]" % 
                                scData.azimuth(pars['tstart'], srcDir))
    notice.notice['COMMENTS'] = 'THIS IS A TEST. REPEAT THIS IS A TEST.'
    
    outfile = pars['name'] + '_Notice.txt'
    notice.write(outfile)

    outfile_location = "'%s'" % os.path.join(output_dir, outfile)
    dbAccess.updateGrb(grb_id, ASP_GCN_NOTICE_DRAFT=outfile_location)

    if Ts_value >= 25:
        #
        # Send this notice for GCN broadcast.
        #
#        mailer = MultiPartMailer("GCN/FERMI_LAT_GND_POSITION")
        mailer = MultiPartMailer("FERMI_LAT_GND_REF_IMPORT")
        mailer.add_text(str(notice.notice))
        mailer.finish()
        mailer.send("jchiang@slac.stanford.edu", ("jchiang@slac.stanford.edu",
                                                  "vxw@capella.gsfc.nasa.gov"))
