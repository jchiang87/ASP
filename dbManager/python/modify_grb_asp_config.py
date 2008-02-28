import databaseAccess as dbAccess

sql = "insert into GRB_ASP_CONFIG (ID, STARTDATE, ENDDATE, IRFS, PARTITIONSIZE, THRESHOLD, DEADTIME, TIMEWINDOW, RADIUS, AGTIMESCALE, AGRADIUS, OPTIMIZER) values (%i, %i, %i, '%s', %i, %i, %i, %i, %i, %i, %i, '%s')" % (2, 257300530, 258595200, 'P5_v0_transient', 30, 120, 1000, 100, 15, 18000, 15, 'Minuit')

dbAccess.apply(sql)
