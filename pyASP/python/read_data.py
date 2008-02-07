"""
@brief Return a tuple of numarrays, one for each column of ASCII data
in file.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import numarray as num

def _readlines(fileobj, comment=''):
    lines = []
    for line in fileobj:
        if ((comment != '' and line.find(comment) == 0)
            or len(line.strip()) == 0):
            continue
        if comment != '':
            line = line.split(comment)[0].strip()
        lines.append(line)
    return lines

def read_data(file, delimiter=None, nskip=0, ncols=0, nmax=0, comment="#"):
    data = _readlines(open(file), comment=comment)
    if nmax == 0:
        nmax = len(data) - nskip
    data = data[nskip:nskip+nmax]
    if ncols == 0:
        ncols = len(data[0].split(delimiter))
    columns = []
    for i in range(ncols):
        columns.append([])
    for line in data:
        datum = line.split(delimiter)
        for i in range(ncols):
            if (datum[i].find('.') == -1 and datum[i].find('e') == -1
                and datum[i].find('E') == -1):
                columns[i].append(int(datum[i]))
            else:
                columns[i].append(float(datum[i]))
    for i in range(ncols):
        columns[i] = num.array(columns[i])
    return tuple(columns)

class AsciiTuple(dict):
    def __init__(self, infile, colnames, **kywds):
        dict.__init__(self)
        self.colnames = colnames
        try:
            kywds.pop('ncols')
        except KeyError:
            pass
        data = read_data(infile, ncols=len(colnames), **kywds)
        for key, column in zip(colnames, data):
            self[key] = column
    def row(self, i, tup=False):
        if tup:
            return tuple([self[item][i] for item in self.colnames])
        class Row:
            pass
        my_row = Row()
        for item in self.colnames:
            my_row.__dict__[item] = self[item][i]
        return my_row

if __name__ == '__main__':
    for foo in zip(*read_data('rois.txt')):
        print foo
