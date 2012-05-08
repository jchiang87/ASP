#!/usr/bin/env python
"""
Read in a series of FITS table files and make them accessible as
numpy arrays

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Id$
#

class FitsNTupleError(RuntimeError):
    "Error reading in FITS table"

class FitsNTuple:
    def __init__(self, fitsfiles, extension=1):
        import sys, pyfits
        import numpy as num
        cat = num.concatenate
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
        for i, file in enumerate(fitsfiles):
            #print "adding", file
            table = pyfits.open(file.strip(" "))
            if table[extension].size() == 0:
                raise FitsNTupleError("zero rows in %s[%s]" % (file.strip(" "),
                                                               extension))
            if i == 0:
                self.names = table[extension].columns.names
            for name in self.names:
                myData = table[extension].data.field(name)
                #
                # These casts to generic data types are necessary to
                # work with swig-wrapped C++ code.  This is required
                # for numpy/pyfits for some reason.
                #
                if myData.dtype.name.find('float') == 0:
                    myData = num.array(myData, dtype=num.float)
                if myData.dtype.name.find('int') == 0:
                    myData = num.array(myData, dtype=num.int)
                if i == 0:
                    columnData[name] = myData
                else:
                    columnData[name] = cat((columnData[name], myData))
        #
        # Add these columns to the internal dictionary.
        #
        self.__dict__.update(columnData)
