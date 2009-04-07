"""
@brief Abstraction for both text and db versions of GCN Notices.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os
import numpy as num
import pyASP
from GcnPacket import GcnPacket
import databaseAccess
from dbAccess import readGcnNotices, grbName

class GcnNotice(object):
    def __init__(self, grb_id, skipped=(),
                 connection=databaseAccess.asp_default):
        """
        GCN Notice summary from packet with smallest positional error radius.
        Allow certain notice types to be skipped.
        """
        self.skipped = skipped
        self._accessDb(grb_id, connection)
        self.ft2 = None
    def _accessDb(self, grb_id, connection):
        #
        # Use trigger time from initial notice and best position 
        # based on error circle radius.
        #
        print "GcnNotice._accessDb: grb_id = ", grb_id
        notice_list = readGcnNotices(grb_id, skipped=self.skipped,
                                     connection=connection)
        packet_list = [GcnPacket(x.tostring()) for x in notice_list]
        my_packet = packet_list[0]
        #
        # Use MET of initial notice as burst start time.
        #
        self.start_time = my_packet.MET
        errMin = my_packet.posError
        for item in packet_list:
            if item.posError < errMin:
                errMin = item.posError
                my_packet = item
        self.packet = my_packet
        self.RA = my_packet.RA
        self.DEC = my_packet.Dec
        self.LOC_ERR = my_packet.posError
        self.Name = grbName(grb_id)
    def _parseTextFile(self, infile):
        self._create_dict(infile)
        self.RA = self._readcoord('GRB_RA')
        self.DEC = self._readcoord('GRB_DEC')
        self.LOC_ERR = self._readfloat('GRB_ERROR')/60.
        tjd = self._readfloat('GRB_DATE')
        sod = self._readfloat('GRB_TIME')
        jd = pyASP.JulianDate(tjd + 2440000.5 + sod/8.64e4)
        self.start_time = (jd.seconds() -
                           pyASP.JulianDate_missionStart().seconds())
        year, month, day, hours = jd.gregorianDate()
        self.Name = ('GRB%02i%02i%02i%03i' %
                     (year % 100, month, day, hours/24.*1000))
        self.ft2 = None
    def _create_dict(self, infile):
        self._dict = {}
        for line in open(infile):
            if line.find('COMMENTS') == 0:
                break
            if line.find(':') > 0:
                key = line.split(':')[0]
                self._dict[key] = line.strip()
    def _readcoord(self, key):
        line = self._dict[key]
        return float(line.split(':')[1].split('d')[0].strip("+"))
    def _readfloat(self, key):
        line = self._dict[key]
        return float(line.split(':')[1].split()[0])
    def offAxisAngle(self, ft2File, radec=None):
        self._getFt2(ft2File)
        indx = num.where(self.ft2.START > self.start_time)
        ii = indx[0][0]
        dir1 = pyASP.SkyDir(self.ft2.RA_SCZ[ii-1], self.ft2.DEC_SCZ[ii-1])
        dir2 = pyASP.SkyDir(self.ft2.RA_SCZ[ii], self.ft2.DEC_SCZ[ii])
        t1 = self.ft2.START[ii-1]
        t2 = self.ft2.START[ii]
        my_dir = pyASP.SkyDir_interpolate(dir1, dir2, t1, t2, self.start_time)
        if radec is None:
            radec = self.RA, self.DEC
        return my_dir.difference(pyASP.SkyDir(*radec))*180./num.pi
    def inSAA(self, ft2File):
        self._getFt2(ft2File)
        indx = num.where(self.ft2.START < self.start_time)
        ii = indx[0][-1]
        return self.ft2.IN_SAA[ii]
    def _getFt2(self, ft2File):
        if self.ft2 is None:
            from FitsNTuple import FitsNTuple
            self.ft2 = FitsNTuple(ft2File, 'SC_DATA')
    def __repr__(self):
        return self.Name

if __name__ == '__main__':
    notice_path = '/nfs/farm/g/glast/u33/jchiang/ASP/GRB/Notices'
    notice = GcnNotice(os.path.join(notice_path, 'GBM_Notice_080101283.txt'))
    print notice.RA, notice.DEC, notice.LOC_ERR, notice.start_time, \
          notice.Name
