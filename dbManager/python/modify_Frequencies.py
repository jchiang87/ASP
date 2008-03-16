import databaseAccess as dbAccess

#sql = "delete from FREQUENCIES where FREQUENCY='downlink'"

#sql = "insert into FREQUENCIES (FREQUENCY) values ('six_hour')"
#dbAccess.apply(sql, connection=dbAccess.glastdev)
#sql = "insert into FREQUENCIES (FREQUENCY) values ('daily')"
#dbAccess.apply(sql, connection=dbAccess.glastdev)
#sql = "insert into FREQUENCIES (FREQUENCY) values ('weekly')"
#dbAccess.apply(sql, connection=dbAccess.glastdev)

#sql = "select * from FREQUENCIES"
#def getFrequencies(cursor):
#    freqs = []
#    for entry in cursor:
#        freqs.append(entry[0])
#    return freqs
#
#foo = dbAccess.apply(sql, getFrequencies, dbAccess.glastdev)
#print foo

## May 16, 2008 = 232588800.0 MET
#
#met = 232588800

#met = 257731200    # earliest MET of OpsSim2
met = 257745510    # earliest valid MET of OpsSim2

def insertInterval(id, freq, tstart, tstop):
    sql_template = ("insert into TIMEINTERVALS (INTERVAL_NUMBER, FREQUENCY, "
                    + "TSTART, TSTOP) values (%i, '%s', %i, %i)")
    sql = sql_template % (id, freq, tstart, tstop)
    dbAccess.apply(sql, connection=dbAccess.asp_dev)

def deleteInterval(id, freq):
    sql = "delete from TIMEINTERVALS where INTERVAL_NUMBER=%i and FREQUENCY='%s'" % (id, freq)
    dbAccess.apply(sql, connection=dbAccess.asp_dev)

#insertInterval(1, 'six_hour', met - 6*3600, met)
deleteInterval(1, 'daily')
insertInterval(1, 'daily', met - 86400, met)
#insertInterval(1, 'weekly', met - 7*8.64e4, met)
#
#deleteInterval(0, 'six_hour')
#deleteInterval(0, 'weekly')
