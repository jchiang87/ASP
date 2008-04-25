"""
@brief Implementation of Jay and Jerry's GRB blind search algorithm.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
import pipeline
import numpy as num
    
from grbASP import Event, EventClusters, PsfClusters, ScData, SkyDir
from FitsNTuple import FitsNTuple

def convert(events, imin=0, imax=None):
    if imax is None:
        imax = len(events.RA)
    my_events = []
    for evt_tuple in zip(events.RA[imin:imax], events.DEC[imin:imax],
                         events.TIME[imin:imax], events.ENERGY[imin:imax],
                         events.EVENT_CLASS[imin:imax]):
        my_events.append(Event(*evt_tuple))
    if len(my_events) == 0:
        raise RuntimeError, "zero events in tuple"
    return my_events

def triggerTimes(time, logLike, threshold=112, deadtime=0):
    """Find trigger times and peak times based on a time-ordered
    figure-of-merit (FOM), such as Jay and Jerry's -log(likelihood).
    Return the initial time the FOM is above threshold, resetting the
    trigger when the FOM goes back below threshold or after an
    artificial deadtime."""
    triggers = []
    tpeaks = []
    ll_values = []
    trigger_is_set = True
    lmax = 0
    tmax = time[0]
    for tt, ll in zip(time, logLike):
        if (trigger_is_set and ll > threshold and
            (len(triggers) == 0 or (tt - triggers[-1]) > deadtime)):
            triggers.append(tt)
            trigger_is_set = False
        if not trigger_is_set:
            if ll > lmax:
                lmax = ll
                tmax = tt
        if not trigger_is_set and ll <= threshold:
            tpeaks.append(tmax)
            ll_values.append(lmax)
            lmax = 0
            trigger_is_set = True
    return triggers, tpeaks, ll_values

def downlink_bg_rate(events, imin, imax):
    times = events.TIME
    offset = 0
    localmin = max(0, imin - offset)
    localmax = min(len(times)-1, imax + offset)
    return (localmax - localmin)/(times[localmax] - times[localmin])

class BlindSearch(object):
    def __init__(self, events, clusterAlg, dn=30, deadtime=1000, threshold=110,
                 bg_rate=0):
        """events is a FitsNTuple of an FT1 file(s);
        dn is the number of consecutive events (in time) to consider;
        deadtime is the time in seconds to wait for the current trigger state
           to expire (for long bursts or Solar flares);
        threshold is the trigger threshold in terms of -log-likelihood for
           identifying a burst;
        clusterAlg is the clustering algorithm, either EventClusters to use
           JPN and JB's algorithm or PsfClusters to use the Psf.
        """
        self.clusterAlg = clusterAlg 
        self.events = events
        nevts = len(events.RA)
        dnevts = int(dn)
        if dnevts <= 0:
            raise ValueError, "Cannot have partition size <= 0"
        indices = range(0, nevts, dnevts)
        indices.append(nevts)
        if indices[-1]-1 == indices[-2]: # handle orphan event
            indices.pop()
            indices[-1] = nevts
        logdts = []
        logdists = []
        times = []
        ras, decs = [], []
        ls, bs = [], []
        mean_bg_rate = nevts/(events.TIME[-1] - events.TIME[0])
        for imin, imax in zip(indices[:-1], indices[1:]):
            try:
                results = clusterAlg.processEvents(convert(events, imin, imax),
                                                   bg_rate)
                (logPdts, logPdists), meanDir = results
                ra, dec = meanDir.ra(), meanDir.dec()
                l, b = meanDir.l(), meanDir.b()
                logdts.append(logPdts)
                logdists.append(logPdists)
                times.append((events.TIME[imin] + events.TIME[imax-1])/2.)
                ras.append(ra)
                decs.append(dec)
                ls.append(l)
                bs.append(b)
            except ValueError:
                pass
        self.times = num.array(times)
        self.logdts = num.array(logdts)
        self.logdists = num.array(logdists)
        self.ras = num.array(ras)
        self.decs = num.array(decs)
        self.glons = num.array(ls)
        self.glats = num.array(bs)
        logLike = self.logdts + self.logdists
        self.triggers, self.tpeaks, self.ll = triggerTimes(times, -logLike,
                                                           deadtime=deadtime,
                                                           threshold=threshold)
    def grbDirs(self, radius=5):
        """Go through the list of candidate bursts, and return a list
        of SkyDirs, event (ras, decs), and peak times.
        """
        events = self.events
        grb_dirs = []
        for tpeak, ll in zip(self.tpeaks, self.ll):
            time = num.array(events.TIME)
            imin = min(num.where(time > tpeak-50)[0])
            imax = max(num.where(time < tpeak+50)[0])
            imin, imax = self._temper(imin, imax)
            try:
                results = self.clusterAlg.processEvents(convert(events,
                                                                imin, imax))
                grb_dir = [results[1]]
                grb_dir.append(tpeak)
                grb_dir.append(ll)
                grb_dirs.append(grb_dir)
            except:
                pass
        return grb_dirs
    def _temper(self, imin, imax, limit=100):
        if imax - imin > limit:
            midpoint = (imin + imax)/2
            return midpoint - limit/2, midpoint + limit/2
        else:
            return imin, imax

def read_gtis(ft1files):
    data = FitsNTuple(ft1files, 'GTI')
    gtis = []
    for start, stop in zip(data.START, data.STOP):
        gtis.append((start, stop))
    return gtis

def gti_bounds(events, gtis):
    imins, imaxs = [], []
    for tmin, tmax in gtis:
        imins.append(num.where(events.TIME >= tmin)[0][0])
        imaxs.append(num.where(events.TIME <= tmax)[0][-1])
    return imins, imaxs

def zenmax_filter(tup, zmax=100):
    indx = num.where(tup.ZENITH_ANGLE < zmax)
    for name in tup.names:
        tup.__dict__[name] = num.array(tup.__dict__[name])
        tup.__dict__[name] = tup.__dict__[name][indx]
    return tup

class Foo(object):
    def __init__(self):
        pass

class PackagedEvents(object):
    def __init__(self, events):
        self.events = events
    def __call__(self, imin, imax):
        foo = Foo()
        for name in self.events.names:
            foo.__dict__[name] = self.events.__dict__[name][imin:imax]
        return foo

if __name__ == '__main__':
    import os, shutil
    import sys
    from LatGcnNotice import LatGcnNotice
    from GrbAspConfig import grbAspConfig
    import grb_followup
    import dbAccess
    from FileStager import FileStager
    from getFitsData import filter_versions
    
    grbroot_dir = os.path.abspath(os.environ['GRBROOTDIR'])

    fileStager = FileStager("GRB_blind_search/%s" % os.environ['DownlinkId'],
                            stageArea=grbroot_dir, cleanup=True,
                            messageLevel='DEBUG')

    ft1_files = [x.strip().strip('+') for x in open('Ft1FileList')]
    print ft1_files
    ft1_files = filter_versions(ft1_files)
    print "staging files:"
    for item in ft1_files:
        print item
    downlink_files = fileStager.infiles(ft1_files)

    os.chdir(grbroot_dir)  # move to the working directory

    raw_events = FitsNTuple(downlink_files)
    print "Number of events read: ", len(raw_events.TIME)
    print "from FT1 files: ", downlink_files
    raw_events = zenmax_filter(raw_events)

    gtis = read_gtis(downlink_files)
    clusterAlg = EventClusters(gtis)

    imins, imaxs = gti_bounds(raw_events, gtis)

    package = PackagedEvents(raw_events)

    for imin, imax in zip(imins, imaxs):
        events = package(imin, imax)
        grbConfig = grbAspConfig.find(min(events.TIME))

        blindSearch = BlindSearch(events, clusterAlg, 
                                  dn=grbConfig.PARTITIONSIZE,
                                  deadtime=grbConfig.DEADTIME, 
                                  threshold=grbConfig.THRESHOLD)

        grbDirs = blindSearch.grbDirs()
        for item in grbDirs:
            grb_dir, tpeak, ll = item
            notice = LatGcnNotice(tpeak, grb_dir.ra(), grb_dir.dec())
            #
            # Need better logic to check if this burst already has a
            # Notice from a different mission/instrument. Here we just
            # check that the grb_id (int(MET of burst)) hasn't already
            # been used by an entry in the GRB database table.
            #
            isUpdate = dbAccess.haveGrb(notice.grb_id)
            notice.registerWithDatabase(isUpdate=isUpdate)
            #notice.email_notification()
            grb_output = os.path.join(grbroot_dir, `notice.grb_id`)
            try:
                os.mkdir(grb_output)
                os.chmod(grb_output, 0777)
            except OSError:
                if os.path.isdir(grb_output):
                    os.chmod(grb_output, 0777)
                else:
                    raise OSError, "Error creating directory: " + grb_output
            outfile = os.path.join(grb_output, notice.name + '_Notice.txt')
            notice.setTriggerNum(tpeak)
            notice.addComment(', '.join(downlink_files))
            notice.write(outfile)
            os.chmod(outfile, 0666)
            print grb_dir.ra(), grb_dir.dec(), tpeak
        
    grb_followup.handle_unprocessed_events(grbroot_dir)
