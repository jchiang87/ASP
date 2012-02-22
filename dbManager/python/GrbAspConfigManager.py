"""
@file GrbAspConfigManager.py
@brief Functions to manage the entries in the grb_asp_config table.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import copy
import databaseAccess as dbAccess

_defaultConfig = {"STARTDATE" : 257300530,
                  "ENDDATE" : 258595200,
                  "IRFS" : "'P5_v0_transient'",
                  "PARTITIONSIZE" : 30,
                  "THRESHOLD" : 120,
                  "DEADTIME" : 1000,
                  "TIMEWINDOW" : 100,
                  "RADIUS" : 15,
                  "AGTIMESCALE" : 18000,
                  "AGRADIUS" : 15,
                  "OPTIMIZER": "'Minuit'"}

def default():
    return copy.copy(_defaultConfig)

def insertEntry(id):
    sql = "insert into GRB_ASP_CONFIG (ID) values (%i)" % id
    print sql
    dbAccess.apply(sql)

def updateEntry(id, config):
    assignments = ",".join(["%s=%s" % (key, config[key]) for key in config])
    sql = "update GRB_ASP_CONFIG set %s where ID=%i" % (assignments, id)
    print sql
    dbAccess.apply(sql)

def deleteEntry(id):
    sql = "delete from GRB_ASP_CONFIG where ID=%i" % id
    dbAccess.apply(sql)
