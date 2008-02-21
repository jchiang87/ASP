#!/usr/bin/env python
"""
Read in a series of FITS table files and make them accessible as
numpy arrays

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Id$
#

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
