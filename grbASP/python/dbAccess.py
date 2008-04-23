"""
@brief Functions to access GRB database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import datetime
import time
import array
import base64
from databaseAccess import apply, cx_Oracle

def convert_clob(clob):
    foo = array.array('l', base64.decodestring(clob.read()))
    return foo

def readGrb(grb_id):
    sql = "select * from GRB where GRB_ID = %i" % grb_id
    def cursorFunc(cursor):
        for item in cursor:
            return item
        return []
    return apply(sql, cursorFunc)

def getGrbIds():
    sql = "select * from GRB"
    def cursorFunc(cursor):
        grb_ids = []
        for item in cursor:
            grb_ids.append(item[0])
        return grb_ids
    return apply(sql, cursorFunc)

def readGcnNotices(grb_id):
    sql = "select * from GCNNOTICES where GRB_ID = %i" % grb_id
    def cursorFunc(cursor):
        notices = []
        for entry in cursor:
            data = [x for x in entry]
            data[1] = convert_clob(data[1])
            notices.append(data)
        return notices
    return apply(sql, cursorFunc)

def deleteNotice(grb_id):
    sql = "delete from GCNNOTICES where GRB_ID = %i" % grb_id
    apply(sql)

def deleteAfterglow(grb_id):
    sql = "delete from GRBAFTERGLOW where GRB_ID = %i" % grb_id
    apply(sql)

def deleteGrb(grb_id):
    deleteNotice(grb_id)
    deleteAfterglow(grb_id)
    sql = "delete from GRB where GRB_ID = %i" % grb_id
    apply(sql)

def insertGrb(grb_id):
    sql = "insert into GRB (GRB_ID) values (%i)" % grb_id
    apply(sql)

def insertAfterglow(grb_id):
    sql = "insert into GRBAFTERGLOW (GRB_ID) values (%i)" % grb_id
    apply(sql)

def insertGcnNotice(grb_id, gcn_notice, notice_date, met, ra, dec, error,
                    isUpdate=0):
    notices = readGcnNotices(grb_id)
    for notice in notices:
        if notice == gcn_notice:
            # This GCN Notice associated with this grb_id is already
            # in the database table.
            return
    sql = (("insert into GCNNOTICES (GRB_ID, GCN_NOTICE, NOTICEDATE, "
            + "NOTICEMET, RA, DEC, ERROR, ISUPDATE) values "
            + "(%i, '%s', SYS_EXTRACT_UTC(current_timestamp), %i, "
            + "%.5f, %.5f, %.5f, %i)")
           % (grb_id, base64.encodestring(gcn_notice.tostring()), 
              met, ra, dec, error, isUpdate))
    apply(sql)

def updateGrb(grb_id, **kwds):
    assignments = ["%s=%s" % (key, kwds[key]) for key in kwds]
    sql = ("update GRB set %s where GRB_ID = %i" 
           % (','.join(assignments), grb_id))
    print "updateGrb sql = "
    print sql
    apply(sql)

def updateAfterglow(grb_id, **kwds):
    assignments = ["%s=%s" % (key, kwds[key]) for key in kwds]
    sql = ("update GRBAFTERGLOW set %s where GRB_ID = %i" 
           % (','.join(assignments), grb_id))
    apply(sql)

def current_date():
    data = time.gmtime()
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec')
    year = data[0]
    month = data[1] - 1
    day = data[2]
    date = "%4i-%s-%02i 10:11:00" % (year, months[month], day)
    print date
    return date
#    return "%02i %s %i" % (day, months[month], year)
#    return `datetime.datetime(*data[:6])`

def simple_packet(type):
    my_packet = array.array("l", (type,) + 39*(0,))
    my_packet.byteswap()
    return my_packet

if __name__ == '__main__':
    grb_id = 1234

    try:
        deleteGrb(grb_id)
    except:
        pass

    insertGrb(grb_id)
    insertGcnNotice(grb_id, simple_packet(6), current_date(), 0, 
                    193.98, -5.82, 1)

    notices = readGcnNotices(grb_id)
    for notice in notices:
        notice[1].byteswap()
        print notice

    print readGrb(grb_id)

    updateGrb(grb_id, LAT_GRB_ID=111, LAT_RA=121.3, GBM_CAT_ID="'foo'",
              GCN_NAME="'GRB07010100'")
    print readGrb(grb_id)
    print readGrb(grb_id)[1]

    print getGrbIds()
