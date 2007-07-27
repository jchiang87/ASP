import os
import numarray as num
import pyASP

_LatFt2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'

class GcnNotice(object):
    def __init__(self, infile):
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
    def __repr__(self):
        return self.Name

if __name__ == '__main__':
    from GbmNotice import GbmNotice
    
    notice_path = '/nfs/farm/g/glast/u33/jchiang/ASP/GRB/Notices'
    notice = GcnNotice(os.path.join(notice_path, 'GBM_Notice_080101283.txt'))

    old_notice = GbmNotice(os.path.join(notice_path,
                                        'GLG_NOTICE_080101283.TXT'))
    print notice.RA, notice.DEC, notice.LOC_ERR, notice.start_time, \
          notice.Name
    print old_notice.RA, old_notice.DEC, old_notice.LOC_ERR, \
          old_notice.start_time, old_notice.Name
