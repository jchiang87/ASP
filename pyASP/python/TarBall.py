"""
@brief Tarball class for packing up ASP results and archiving on xrootd.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import os

class FilenameConflictError(RuntimeError):
    "File name conflict"

class TarBall(object):
    def __init__(self, filename, verbose=True, clobber=True):
        self.filename = filename
        self.verbose = verbose
        self.clobber = clobber
        if os.path.isfile(self.filename):
            if clobber:
                os.remove(self.filename)
            else:
                message = "Archive %s already exists." % self.filename
                raise FilenameConflictError(message)
    def append(self, files):
        if self.verbose:
            print "appending %s" % files
        if os.path.isfile(self.filename):
            os.system('tar rf %s %s' % (self.filename, files))
        else:
            os.system('tar cf %s %s' % (self.filename, files))
    def gzip(self):
        if self.verbose:
            print "gzipping %s..." % self.filename
        target = "%s.gz" % self.filename
        if os.path.isfile(target):
            if self.clobber:
                os.remove(target)
            else:
                message = "Cannot gzip: %s already exists." % target
                raise FilenameConflictError(message)
        os.system('gzip %s' % self.filename)

if __name__ == '__main__':
    import glob

    archive_name = 'DRP_%s_%s.tar' % tuple(os.getcwd().split('/')[-2:])
    targets = ('rois.txt', 
               'point_sources.xml',
               'FT2_merged.fits')
    region_targets = ('region???_*_model.xml',
                      'events_100_300000.fits',
                      'expCube.fits',
                      'expMap_sum.fits',
                      'analysis*.py')

    regions = glob.glob('region*')
    regions.sort()
               
    my_tarball = TarBall(archive_name)
    for target in targets:
        my_tarball.append(target)
    for region in regions:
        for item in region_targets:
            target = os.path.join(region, item)
            my_tarball.append(target)

    my_tarball.gzip()
