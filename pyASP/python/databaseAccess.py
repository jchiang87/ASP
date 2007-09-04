"""
@brief Function to access ORACLE database tables.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import cx_Oracle

_connect_args = ("glastgen", "glast06", "GLASTP")

def nullFunc(*args):
    return None

def apply(sql, cursorFunc=nullFunc):
    my_connection = cx_Oracle.connect(*_connect_args)
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
