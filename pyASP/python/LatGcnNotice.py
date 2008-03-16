"""
@brief Encapsulation of a LAT GCN Notice.  The format is based on that
of the GBM GCN Notices.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import pyASP

_LAT_Notice = """GLAST LAT BURST NOTIFICATION
**************************************

BURST Name     =                         %s
BURST Date     =                         %s
BURST Time (Sec of Day)     =            %s
BURST RA  (Deg)   =                      %.3f
BURST DEC (Deg)  =                       %.3f
BURST LOC ERR (Deg 1 sigma)  =           """

class LatGcnNotice(object):
    def __init__(self, burstTime, ra, dec):
        jd = pyASP.jd_from_MET(burstTime)
        year, month, day, hours = jd.gregorianDate()
        date = '%02i%02i%02i' % ((int(year) % 100), int(month), int(day))
        time = '%.1f' % (hours*3600.,)
        name = 'GRB%s%03i' % (date, 1000.*hours/24.)
        self.name = name
        self.text = _LAT_Notice % (name, date, time, ra, dec)
    def setLocErr(self, error):
        self.text + (".6f" % error)
    def write(self, outfile):
        output = open(outfile, 'w')
        output.write(self.text + '\n')
        output.close()

if __name__ == '__main__':
    notice = LatGcnNotice(222535575.0, 305.723, -67.0446)
    print notice.text
