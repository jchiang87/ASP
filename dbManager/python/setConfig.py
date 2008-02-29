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

rootPath = lambda x : os.path.join(os.environ['DBMANAGERROOT'], 'data', x)
srcModel = rootPath('AspSrcModel.xml')
try:
    insertSources(srcModel)
except StandardError, message:
    print "StandardError caught: ", message

grbConfig = GrbAspConfigManager.default()

id = 0
grbConfig['STARTDATE'] = date2met("2009-03-02")
grbConfig['ENDDATE'] = date2met("2009-03-16")

try:
    GrbAspConfigManager.insertEntry(id)
except StandardError, message:
    print "StandardError caught: ", message

GrbAspConfigManager.updateEntry(id, grbConfig)

