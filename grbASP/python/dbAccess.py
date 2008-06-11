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
from databaseAccess import apply, cx_Oracle, asp_default, glastgen

def convert_clob(clob):
    foo = array.array('l', base64.decodestring(clob.read()))
    return foo

def haveGrb(grb_id):
    "Return true if desired GRB_ID is in the GRB table"
    sql = "select GRB_ID from GRB where GRB_ID = %i and GCAT_FLAG=0" % grb_id
    def cursorFunc(cursor):
        for item in cursor:
            return True
        return False
    return apply(sql, cursorFunc)

def gcnTriggerTimes(mission, trigger_num):
    """Find the GCN notices with matching mission and trigger number fields
    and return the sorted "trigger" times."""
    sql = ("select GRB_ID, NOTICEMET from GCNNOTICES " +
           "where MISSION='%s' " % mission +
           "and TRIGGER_NUM=%i" % trigger_num)
    noticemets = apply(sql, lambda curs : [x for x in curs])
    noticemets.sort()
    return noticemets

def grbName(grb_id):
    sql = "select GCN_NAME from GRB where GRB_ID=%i and GCAT_FLAG=0" % grb_id
    def getName(cursor):
        for item in cursor:
            return item[0]
    return apply(sql, getName)

def getGrbIds():
    sql = "select GRB_ID from GRB where GCAT_FLAG=0"
    def cursorFunc(cursor):
        grb_ids = []
        for item in cursor:
            grb_ids.append(item[0])
        return grb_ids
    return apply(sql, cursorFunc)

def readGcnNotices(grb_id):
    """Return the stored packet buffers from the GCNNOTICES table, with
    the initial notice being returned first in the list."""
    sql = "select GCN_NOTICE from GCNNOTICES where GRB_ID = %i order by ISUPDATE ASC" % grb_id
    def cursorFunc(cursor):
        notices = []
        for entry in cursor:
            notices.append(convert_clob(entry[0]))
        return notices
    return apply(sql, cursorFunc)

def deleteNotice(grb_id):
    sql = "delete from GCNNOTICES where GRB_ID = %i" % grb_id
    apply(sql)

def deleteAfterglow(grb_id):
    sql = "delete from GRB where GRB_ID = %i and GCAT_FLAG=1" % grb_id
    apply(sql)

def deleteGrb(grb_id):
    deleteNotice(grb_id)
    deleteAfterglow(grb_id)
    sql = "delete from GRB where GRB_ID = %i" % grb_id
    apply(sql)

def insertGrb(grb_id):
    sql = "insert into GRB (GRB_ID, GCAT_FLAG) values (%i, 0)" % grb_id
    apply(sql)

def insertAfterglow(grb_id):
    sql = "insert into GRB (GRB_ID, GCAT_FLAG) values (%i, 1)" % grb_id
    apply(sql)

def insertGcnNotice(grb_id, gcn_notice, mission, trigger_num, 
                    notice_date, met, ra, dec, error,
                    isUpdate=0, notice_type="None"):
    notices = readGcnNotices(grb_id)
    for notice in notices:
        if notice == gcn_notice:
            # This GCN Notice associated with this grb_id is already
            # in the database table.
            return
    sql = "select gcnnotices_seq.nextval from dual"
    def getId(cursor):
        for entry in cursor:
            return entry[0]
    gcnnotice_id = apply(sql, getId)
    sql = ("insert into GCNNOTICES values(:gcnnotice_id, :grb_id, " + 
           ":gcat_flag, :gcn_notice, :mission, :noticetype, :trigger_num, " +
           ":noticedate, :noticemet, " + 
           ":ra, :dec, :error, :isupdate, :adv_comment, :adv_name)")
    args = {"gcnnotice_id" : gcnnotice_id,
            "grb_id" : grb_id,
            "gcat_flag" : 0,
            "gcn_notice" : base64.encodestring(gcn_notice.tostring()),
            "mission" : mission,
            "noticetype" : notice_type,
            "trigger_num" : trigger_num,
            "noticedate" : notice_date,
            "noticemet" : met,
            "ra" : ra,
            "dec" : dec,
            "error" : error, 
            "isupdate" : isUpdate,
            "adv_comment" : None,
            "adv_name" : None}
    my_connection = cx_Oracle.connect(*asp_default)
    cursor = my_connection.cursor()
    cursor.execute(sql, args)
    cursor.close()
    my_connection.commit()
    my_connection.close()

def updateGrb(grb_id, **kwds):
    assignments = ["%s=%s" % (key, kwds[key]) for key in kwds]
    sql = ("update GRB set %s where GRB_ID = %i and GCAT_FLAG=0" 
           % (','.join(assignments), grb_id))
    print "updateGrb sql = "
    print sql
    apply(sql)

def updateAfterglow(grb_id, **kwds):
    assignments = ["%s=%s" % (key, kwds[key]) for key in kwds]
    sql = ("update GRB set %s where GRB_ID = %i and GCAT_FLAG=1" 
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

def simple_packet(type):
    my_packet = array.array("l", (type,) + 39*(0,))
    my_packet.byteswap()
    return my_packet

def grbAdvocateEmails():
    sql = """select u.first_name,u.last_name,u.email from profile_user u
         join profile_ug ug on ug.user_id=u.user_name 
         where group_id in
         (select group_name from profile_group 
          left outer join profile_gg on parent_id = group_name 
          start with group_name='GRBAdvocate' 
          connect by prior group_name = child_id)
         group by u.first_name,u.last_name,u.email"""
    try:
        email_list = apply(sql, lambda curs : [x[2] for x in curs], 
                           connection=glastgen)
    except:
        email_list = ['jchiang@slac.stanford.edu']
    return email_list

if __name__ == '__main__':
    grb_id = 1234

    try:
        deleteGrb(grb_id)
    except:
        pass

    insertGrb(grb_id)
    insertGcnNotice(grb_id, simple_packet(6), "GLAST", grb_id, 
                    current_date(), 0, 
                    193.98, -5.82, 1)

    notices = readGcnNotices(grb_id)
    for notice in notices:
        notice[1].byteswap()
        print notice

    print haveGrb(grb_id)

    updateGrb(grb_id, LAT_GRB_ID=111, LAT_RA=121.3, GBM_CAT_ID="'foo'",
              GCN_NAME="'GRB07010100'")
    print haveGrb(grb_id)

    print getGrbIds()
