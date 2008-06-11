"""
@brief Function to access ORACLE database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import cx_Oracle

if os.environ['ORACLE_HOME'] == '/usr/oracle':
    #
    # Use encoded passwords from config file.
    #
    db_config = open(os.environ['ASP_DB_CONFIG'], 'r')
    lines = db_config.readlines()
    glastgen = lines[0].strip().encode('rot13').split()
    asp_prod = lines[1].strip().encode('rot13').split()
    asp_dev = lines[2].strip().encode('rot13').split()
else:
    # 
    # Use Oracle wallet.
    #
    glastgen = ('/@glastgenprod',)
    asp_prod = ('/@asp',)
    asp_dev = ('/@asp-dev',)

asp_default = asp_dev
#asp_default = asp_prod

def nullFunc(*args):
    return None

def apply(sql, cursorFunc=nullFunc, connection=asp_default):
    my_connection = cx_Oracle.connect(*connection)
    cursor = my_connection.cursor()
    try:
        cursor.execute(sql)
        results = cursorFunc(cursor)
    except cx_Oracle.DatabaseError, message:
        cursor.close()
        my_connection.close()
        raise cx_Oracle.DatabaseError, message
    cursor.close()
    if cursorFunc is nullFunc:
        my_connection.commit()
    my_connection.close()
    return results

def getDbObjects(tablename, connection=asp_default):
    """Return a list of entries for the specified db table"""
    sql = "SELECT * from %s" % tablename
    def cursorFunc(cursor):
        cols = [column[0] for column in cursor.description]
        entries = []
        for item in cursor:
            entries.append(dict(zip(cols, item)))
        return entries
    return apply(sql, cursorFunc, connection)
