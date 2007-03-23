"""
@brief Trending database interface.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import subprocess

class DbEntryError(EnvironmentError):
    "Trending database Error"

class DbEntry(object):
    def __init__(self, source, variable, tstart, tstop, cadence="daily"):
        args = ("/afs/slac/g/glast/ground/bin/createTrendableDataEntry",
                source, variable, cadence, "%i" % tstart, "%i" % tstop)
        self.dataId = self._subprocess(*args)
    def setValues(self, value, error):
        self._subprocess("/afs/slac/g/glast/ground/bin/addTrendableData",
                         self.dataId, "mean", "%s" % value)
        self._subprocess("/afs/slac/g/glast/ground/bin/addTrendableData",
                         self.dataId, "rms", "%s" % error)
    def setMetaData(self, type, value):
        self._subprocess("/afs/slac/g/glast/ground/bin/addTrendableMetaData",
                         self.dataId, type, value)
    def _subprocess(self, *args):
#        self._checkArgs(args)
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err != '':
            raise DbEntryError, err
        return out.strip()
    def _checkArgs(self, args):
        for item in args:
            if item.find(' ') != -1:
                message = ("space found in argument, '%s', " 
                           + "to trending database script") % item
                raise DbEntryError, message
        
if __name__ == '__main__':
    dbEntry = DbEntry("3C_279", "Flux", 0, 86400)
    dbEntry.setValues(100., 13.)
    dbEntry.setMetaData("xmlFile", "srcModel.xml")
    print dbEntry.dataId
