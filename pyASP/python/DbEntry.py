"""
@brief Trending database interface. See 
http://confluence.slac.stanford.edu/display/ISOC/Candidate+Databases+for+ASP 
for a description of the scripts.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import os
#import subprocess

_scriptPath = lambda x : os.path.join("/afs/slac/g/glast/ground",
                                      "sourceMonitoring/bin", x)

class ordered_dict(dict):
    def __init__(self):
        self.my_keys = []
        dict.__init__(self)
    def keys(self):
        return self.my_keys
    def __setitem__(self, key, value):
        if self.my_keys.count(key) == 0:
            self.my_keys.append(key)
        dict.__setitem__(self, key, value)

class DbEntryError(EnvironmentError):
    "Trending database Error"

class DbEntry(object):
    def __init__(self, source, variable, tstart, tstop, cadence="daily"):
        self.args = ordered_dict()
        self.args["sourceName"] = '\"%s\"' % source
        self.args["datatype"] = variable
        self.args["frequency"] = cadence
        self.args["starttime"] = "%i" % tstart
        self.args["endtime"] = "%i" % tstop
        self.args["mean"] = "0"
        self.args["rms"] = "0"
        self.args["isUpperLimit"] = "false"
        self.args["xmlfile"] = "none"
    def setValues(self, value, error, isUpperLimit=False):
        self.args["mean"] = "%s" % value
        self.args["rms"] = "%s" % error
        if isUpperLimit:
            self.args["isUpperLimit"] = "true"
        else:
            self.args["isUpperLimit"] = "false"
    def setXmlFile(self, xmlFile):
        self.args["xmlfile"] = xmlFile
    def write(self, output=None):
        args = [_scriptPath("addSourceMonitoringData")]
        for item in self.args.keys():
            args.append(self.args[item])
        command = " ".join(args)
        message = ""
        if output is None:
            input, output = os.popen4(command)
            for line in output:
                if line.find('Exception') == 0 or len(message) > 0:
                    message += line
            if message:
                raise DbEntryError, message
#            process = subprocess.Popen(args, stdout=subprocess.PIPE,
#                                       stderr=subprocess.PIPE)
#            out, err = process.communicate()
#            if err != '':
#                raise DbEntryError, err
#            return out.strip()
        else:
            output.write("%s\n" % command)
        
if __name__ == '__main__':
    import sys
    drpSources = ["0208-512", 
                  "0235+164",
                  "0827+243",
                  "1406-076", 
                  "1510-089",
                  "1633+382", 
                  "1730-130", 
                  "1ES 1959+650",
                  "1ES 2344+514", 
                  "3C 273",
                  "3C 279", 
                  "3C 454.3", 
                  "BL Lac",
                  "H 1426+428", 
                  "LSI +61 303", 
                  "Mrk 421",
                  "Mrk 501", 
                  "OJ 287",
                  "PKS 0528+134", 
                  "PKS 0716+714", 
                  "PKS 2155-304",
                  "PKS B 1622-297", 
                  "W Comae"]

    start_time = 220838400
    dt = 86400

    for i in range(1):
        tmin = start_time + dt*i
        tmax = tmin + dt
        for source in drpSources:
            dbEntry = DbEntry(source, "flux_100_300000", tmin, tmax)
            dbEntry.setValues(0, 0)
            dbEntry.write(sys.stdout)
#            dbEntry.write()
