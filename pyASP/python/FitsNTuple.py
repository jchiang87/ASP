#!/usr/bin/env python
"""
Read in a series of FITS table files and make them accessible as
numarrays, optionally creating a HippoDraw NTuple.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Id$
#

class FitsNTuple:
    def __init__(self, fitsfiles, extension=1):
        import sys, numarray, pyfits
        cat = numarray.concatenate
        #
        # If fitsfile is not a list or tuple of file names, assume
        # it's a single file name and put it into a single element
        # tuple.
        #
        if type(fitsfiles) != type([]) and type(fitsfiles) != type(()):
            fitsfiles = (fitsfiles, )
        #
        # Process each file named in the list or tuple.
        #
        columnData = {}
        for i, file in zip(xrange(sys.maxint), fitsfiles):
            #print "adding", file
            table = pyfits.open(file.strip(" "))
            if i == 0:
                self.names = table[extension].columns.names
            for name in self.names:
                if i == 0:
                    columnData[name] = table[extension].data.field(name)
                else:
                    columnData[name] = cat((columnData[name],
                                            table[extension].data.field(name)))
        #
        # Add these columns to the internal dictionary.
        #
        self.__dict__.update(columnData)
        
    def makeNTuple(self, name=None, useNumArray=1):
        import hippo, sys, numarray
        if useNumArray:
            nt = hippo.NumArrayTuple()
        else:
            nt = hippo.NTuple()
        if name != None:
            nt.setTitle(name)
        ntc = hippo.NTupleController.instance()
        ntc.registerNTuple(nt)
        for name in self.names:
            if type(self.__dict__[name][0]) == numarray.NumArray:
                columns = self.__dict__[name]
                columns.transpose()
                for i, col in zip(xrange(sys.maxint), columns):
                    colname = "%s%i" % (name, i)
                    nt.addColumn(colname, col)
            else:
                nt.addColumn(name, self.__dict__[name])
        return nt
