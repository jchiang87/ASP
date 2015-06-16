"""
@brief Interface definition and concrete implementation of a function
to fetch L1 data within a given time interval for subsequent analysis.
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

class GetDC2Data(object):
    def __init__(self):
        self._ft2File = '/nfs/farm/g/glast/u33/jchiang/DC2/DC2_FT2_v2.fits'
        self._L1DataPath = '/nfs/farm/g/glast/u33/jchiang/DC2/Downlinks'

        self._dtime = 10800

        self._startTime = 220838400.   # for DC2 data
        #self._startTime = 0.            # for testdata
    def __call__(self, tmin, tmax, l1DataPath=None, ft2File=None,
                 startTime=None):
        "Return full paths to FT1 and FT2 files."
        if l1DataPath is None:
            l1DataPath = self._L1DataPath
        if ft2File is None:
            ft2File = self._ft2File
        if startTime is None:
            startTime = self._startTime
        ifile0 = int((tmin - startTime)/self._dtime)
        ifile1 = int((tmax - startTime)/self._dtime)
        
        ft1Files = []
        for i in range(ifile0, ifile1 + 1):
            ft1Files.append(os.path.join(l1DataPath, 'downlink_%04i.fits' % i))
        
        if len(ft1Files) == 0:
            raise LookupError, ("No FT1 files found for METs %s to %s"
                                % (tmin, tmax))
        return tuple(ft1Files), (ft2File,)

class GetInterleaveData(object):
    def __init__(self):
        self._ft2File = '/nfs/farm/g/glast/u33/omodei/ServiceChallenge2/GleamRun55d/Interleave55d-GR-v11r12-pointing.fits'
        self.sc2_path = '/nfs/farm/g/glast/u26/MC-tasks/CreateFits_Interleave55days/output'
        self.downlinks = self._downlinkFiles()
        self._startTime = 252460800
        self._dtime = 10800
    def _downlinkFiles(self, my_path=None):
        if my_path is None:
            my_path = self.sc2_path
        curdir = os.path.abspath(os.curdir)
        os.chdir(my_path)
        search_string = 'Merit\*.fits'
        input, output = os.popen4('/usr/bin/find . -name %s -print' 
                                  % search_string)
        files = [os.path.join(my_path, line.strip().strip('./')) 
                 for line in output]
        os.chdir(curdir)
        return files
    def __call__(self, tmin, tmax, l1DataPath=None, ft2File=None, 
                 startTime=None):
        if ft2File is None:
            ft2File = self._ft2File
        if startTime is None:
            startTime = self._startTime
        ifile0 = int((tmin - startTime)/self._dtime)
        ifile1 = int((tmax - startTime)/self._dtime)

        ft1Files = self.downlinks[ifile0:ifile1+1]
        
        if len(ft1Files) == 0:
            raise LookupError, ("No FT1 files found for METs %s to %s"
                                % (tmin, tmax))
        return tuple(ft1Files), (ft2File,)

getL1Data = GetDC2Data()
#getL1Data = GetInterleaveData()

if __name__ == '__main__':
    from FitsNTuple import FitsNTuple
    tmin = getL1Data._startTime + 32142
    tmax = getL1Data._startTime + 44213
    ft1, ft2 = getL1Data(tmin, tmax)

    gti = FitsNTuple(ft1[0], 'GTI')
    print ft1[0]
    print gti.START[0], tmin, gti.STOP[-1]
    assert(gti.START[0] < tmin < gti.STOP[-1])

    gti = FitsNTuple(ft1[-1], 'GTI')
    print ft1[-1]
    print gti.START[0], tmax, gti.STOP[-1]
    assert(gti.START[0] < tmax < gti.STOP[-1])
