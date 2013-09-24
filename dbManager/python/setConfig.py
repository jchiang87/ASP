"""
@file setConfig.py

@brief Set the ASP configuration tables in the Oracle database.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
from date2met import date2met
from insertSources import insertSources
import GrbAspConfigManager
import databaseAccess as dbAccess

rootPath = lambda x : os.path.join(os.environ['DBMANAGERROOT'], 'data', x)

#
# POINTSOURCES and DIFFUSESOURCES tables
#
srcModel = rootPath('AspSrcModel.xml')
try:
    insertSources(srcModel)
except StandardError, message:
    print "StandardError caught: ", message

#
# GRB_ASP_CONFIG
#
grbConfig = GrbAspConfigManager.default()

id = 0
grbConfig['STARTDATE'] = date2met("2009-03-02")
grbConfig['ENDDATE'] = date2met("2009-03-16")

try:
    GrbAspConfigManager.insertEntry(id)
except StandardError, message:
    print "StandardError caught: ", message

GrbAspConfigManager.updateEntry(id, grbConfig)

#
# SOURCEMONITORINGCONFIG
#
smConfig = {"SM_CONFIG_ID": 0,
            "STARTDATE" : date2met("2009-03-02"),
            "ENDDATE" : date2met("2009-03-16"),
            "IRFS" : "'P5_v0_source'",
            "ST_VERSION" : "'v9r4p2'",
            "ASP_VERSION" : "'v2'"}

def insertSmConfig(config):
    keys = ",".join(config.keys())
    values = ",".join(["%s" % x for x in config.values()])
    sql = "insert into SOURCEMONITORINGCONFIG (%s) values (%s)" % (keys, values)
    print sql
    try:
        dbAccess.apply(sql)
    except StandardError, message:
        print "Standard Error caught: ", message

insertSmConfig(smConfig)

#
# Set the initial TIMEINTERVALS
#
def insertInterval(id, freq, tstart, tstop):
    sql_template = ("insert into TIMEINTERVALS (INTERVAL_NUMBER, FREQUENCY, "
                    + "TSTART, TSTOP) values (%i, '%s', %i, %i)")
    sql = sql_template % (id, freq, tstart, tstop)
    dbAccess.apply(sql, connection=dbAccess.asp_dev)

#
# This is for AspSims test data
#
id = 1
grbConfig['STARTDATE'] = date2met("2001-01-01")
grbConfig['ENDDATE'] = date2met("2002-01-01")

try:
    GrbAspConfigManager.insertEntry(id)
except StandardError, message:
    print "StandardError caught: ", message

GrbAspConfigManager.updateEntry(id, grbConfig)

smConfig['SM_CONFIG_ID'] = 1
smConfig['STARTDATE'] = date2met('2001-01-01')
smConfig['ENDDATE'] = date2met('2002-01-01')
insertSmConfig(smConfig)

t0 = date2met('2001-01-01')
insertInterval(0, 'six_hours', t0 - 6*3600, t0)
insertInterval(0, 'daily', t0 - 86400, t0)
insertInterval(0, 'weekly', t0 - 7*86400, t0)
