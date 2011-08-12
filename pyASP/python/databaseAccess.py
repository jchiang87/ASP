"""
@brief Function to access ORACLE database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
import cx_Oracle

# 
# Oracle wallet connection strings
#
glastgen = ('/@glastgenprod',)
asp_prod = ('/@asp',)
asp_dev = ('/@asp-dev',)
rsp_prod = ('/@rsp',)
rsp_dev = ('/@rsp-dev',)

#
# Set the default to point to the dev tables.
#
asp_default = asp_dev

try:
    #
    # Reset the default to prod if running in the PROD pipeline.
    #
    if os.environ['PIPELINESERVER'] == "PROD":
        asp_default = asp_prod
except KeyError:
    #
    # We may be running interactively (and did not set PIPELINESERVER), 
    # so keep "DEV" as the default.
    #
    print "Warning: Using dev db tables."
    pass

def nullFunc(*args):
    return None

def apply(sql, cursorFunc=nullFunc, connection=asp_default, args=None):
    my_connection = cx_Oracle.connect(*connection)
    cursor = my_connection.cursor()
    try:
        if args is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)
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
