"""
@brief Return a tuple of numarrays, one for each column of ASCII data
in file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num

def read_data(file, delimiter='', nskip=0, ncols=0, nmax=0, comment="#"):
    data = open(file).readlines()
    if nmax == 0:
        nmax = len(data) - nskip
    data = data[nskip:nskip+nmax]
    if ncols == 0:
        if (delimiter == ''):
            ncols = len(data[0].split())
        else:
            ncols = len(data[0].split(delimiter))
    columns = []
    for i in range(ncols):
        columns.append([])
    for line in data:
        if line.find(comment) == 0:
            continue
        if delimiter == '':
            datum = line.split()
        else:
            datum = line.split(delimiter)
        for i in range(ncols):
            if datum[i].find('.') == -1:
                columns[i].append(int(datum[i]))
            else:
                columns[i].append(float(datum[i]))
    for i in range(ncols):
        columns[i] = num.array(columns[i])
    return tuple(columns)
