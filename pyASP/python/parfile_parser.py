"""
@brief Routine to parse named parameters in a text file as key/value
pairs and return the output as a dict, performing conversions to float
as appropriate.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

def parfile_parser(infile):
    pars = {}
    for line in open(infile).readlines():
        key, value = line.split("=")
        try:
            pars[key.strip()] = float(value.strip())
        except ValueError:
            pars[key.strip()] = value.strip()
    return pars
