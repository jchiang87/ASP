"""
@file date2met.py

@brief Convert Gregorian dates to MET. Based on Nicola's Date2MET.py script.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import datetime
import time

_missionStart = datetime.datetime(2001, 1, 1, 0, 0, 0)

def date2met(datestring=None):
    if datestring is None:
        data = time.gmtime()
        year, month, day, hours, mins, secs = data[:6]
    else:
        year = int(datestring[0:4])
        month = int(datestring[5:7])
        day = int(datestring[8:10])
        try:
            hours = int(datestring[11:13])
            mins = int(datestring[14:16])
            secs = int(datestring[17:19])
        except ValueError:
            hours = 0
            mins = 0
            secs = 0
            pass
    mydate = datetime.datetime(year, month, day, hours, mins, secs)
    diff = mydate - _missionStart
    return diff.days*86400. + diff.seconds

if __name__ == '__main__':
    print date2met("2001-01-01 00 00 00")
    print date2met()
    print date2met("2009-03-03")
