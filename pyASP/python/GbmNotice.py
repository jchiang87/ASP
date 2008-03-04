"""
@brief Encapsulation of information in a GBM notice.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num
import pyASP

_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

class GbmNotice(object):
    _id = {'BURST Name' : 'Name',
           'BURST Date' : 'Date',
           'BURST Time' : 'Time',
           'BURST RA' : 'RA',
           'BURST DEC' : 'DEC',
           'BURST LOC' : 'LOC_ERR',
           'Standard Intensity' : 'Intensity',
           'Closest detectors' : 'Closest_detectors'}
    def __init__(self, infile):
        notice = open(infile)
        for line in notice:
            self._parseLine(line)
        self.start_time = self._convertMET(self.Date, self.Time)
        self.RA = float(self.RA)
        self.DEC = float(self.DEC)
        self.LOC_ERR = float(self.LOC_ERR)
        self.ft2 = None
    def _convertMET(self, date, time):
        year = 2000 + int(date[:2])
        month = int(date[2:4])
        day = int(date[4:6])
        hours = float(time)/3600.
        jd = pyASP.JulianDate(year, month, day, hours)
        return jd.seconds() - pyASP.JulianDate_missionStart().seconds()
    def _parseLine(self, line):
        if line.find('=') != -1:
            fields = line.split()
            self.__dict__[self._id[' '.join(fields[:2])]] = fields[-1]
            if fields[0] == 'Closest':
                self.Closest_detectors = line.split('=')[-1].strip().split()
    def offAxisAngle(self, ft2File=_LatFt2File):
        self._getFt2(ft2File)
        indx = num.where(self.ft2.START > self.start_time)
        ii = indx[0][0]
        dir1 = pyASP.SkyDir(self.ft2.RA_SCZ[ii-1], self.ft2.DEC_SCZ[ii-1])
        dir2 = pyASP.SkyDir(self.ft2.RA_SCZ[ii], self.ft2.DEC_SCZ[ii])
        t1 = self.ft2.START[ii-1]
        t2 = self.ft2.START[ii]
        my_dir = pyASP.SkyDir_interpolate(dir1, dir2, t1, t2,
                                          self.start_time)
        return my_dir.difference(pyASP.SkyDir(self.RA, self.DEC))*180./num.pi
    def inSAA(self, ft2File =_LatFt2File):
        self._getFt2(ft2File)
        indx = num.where(self.ft2.START < self.start_time)
        ii = indx[0][-1]
        return self.ft2.IN_SAA[ii]
    def _getFt2(self, ft2File):
        if self.ft2 is None:
            from FitsNTuple import FitsNTuple
            self.ft2 = FitsNTuple(ft2File, 'SC_DATA')

if __name__ == '__main__':
    import glob
    files = glob.glob('/nfs/farm/g/glast/u33/jchiang/ASP/GRB/Notices/*NOTICE*')
    for item in files:
        notice = GbmNotice(item)
        if notice.offAxisAngle() < 60 and not notice.inSAA():
            print ("%s  %6.2f  %6.2f  %6.2f  %i" %
                   (notice.Name, notice.RA, notice.DEC,
                    notice.offAxisAngle(), notice.inSAA()))
