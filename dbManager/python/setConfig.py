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

keys = ",".join(smConfig.keys())
values = ",".join(["%s" % x for x in smConfig.values()])
sql = "insert into SOURCEMONITORINGCONFIG (%s) values (%s)" % (keys, values)
print sql
dbAccess.apply(sql)
