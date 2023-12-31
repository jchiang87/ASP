"""
@brief Implementation of Jay and Jerry's GRB blind search algorithm.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#
from logProbPlots import createPlots
import os
import shutil
import pipeline
import numpy as num
import pyfits
from GtApp import GtApp
    
from grbASP import Event, EventClusters, ScData, SkyDir
from FitsNTuple import FitsNTuple, FitsNTupleError
from ft1merge import ft2merge
from FileStager import FileStager
from pass_version import EventClassSelection
import celgal
dist = celgal.dist

gtselect = GtApp('gtselect')
gtmktime = GtApp('gtmktime')

def convert(events, imin=0, imax=None):
    if imax is None:
        imax = len(events.RA)
    my_events = []
    for evt_tuple in zip(events.RA[imin:imax], events.DEC[imin:imax],
                         events.TIME[imin:imax], events.ENERGY[imin:imax],
                         events.EVENT_CLASS[imin:imax]):
#        my_events.append(Event(*evt_tuple))
        my_events.append(Event(float(evt_tuple[0]), float(evt_tuple[1]),
                               float(evt_tuple[2]), float(evt_tuple[3]),
#                               int(evt_tuple[4])))
                               0))
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

def local_bg_rate(events, imin, imax, window=100):
    times = events.TIME
    tmin, tmax = times[imin] - window, times[imax-1] + window
    indx1 = num.where(times > tmin)[0][0]
    indx2 = num.where(times < tmax)[0][-1]
    return float(indx2 - indx1)/(times[indx2] - times[indx1])

class BlindSearch(object):
    def __init__(self, events, clusterAlg, dn=30, deadtime=1000, threshold=110,
                 bg_rate=0, bg_window=None):
        """events is a FitsNTuple of an FT1 file(s);
        dn is the number of consecutive events (in time) to consider;
        deadtime is the time in seconds to wait for the current trigger state
           to expire (for long bursts or Solar flares);
        threshold is the trigger threshold in terms of -log-likelihood for
           identifying a burst;
        clusterAlg is the clustering algorithm, in this case, 
           EventClusters to use JPN and JB's algorithm.
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
                if bg_window is not None:
                    bg_rate = local_bg_rate(events, imin, imax, bg_window)
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
            #
            # If this peak value occurs in a data gap greater than
            # +/-50 sec, then imin, imax below will satisfy imax =
            # imin + 1 and will correspond to an empty tuple.
            # convert(...) will raise an exception and this candidate
            # value will be skipped.  This is the desired behavior,
            # but the peak value will still be retained in the logProb
            # output file.
            #
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
            except Exception, message:
                print message
                pass
        return grb_dirs
    def _temper(self, imin, imax, limit=100):
        if imax - imin > limit:
            midpoint = (imin + imax)/2
            return midpoint - limit/2, midpoint + limit/2
        else:
            return imin, imax

def writeTimeHistory(times, logdts, logdists, outfile):
    time = pyfits.Column(name="time", format="D", array=times)
    logdt = pyfits.Column(name="logL_temporal", format="D", array=logdts)
    logdist = pyfits.Column(name="logL_spatial", format="D", array=logdists)
    output = pyfits.HDUList()
    output.append(pyfits.PrimaryHDU())
    output.append(pyfits.new_table((time, logdt, logdist)))
    output[1].name = "LogProbabilities"
    output.writeto(outfile, clobber=True)

def read_gtis(ft1files):
    data = FitsNTuple(ft1files, 'GTI')
    gtis = []
    for start, stop in zip(data.START, data.STOP):
        gtis.append((start, stop))
    return gtis

def gti_bounds(events, gtis):
    imins, imaxs = [], []
    for tmin, tmax in gtis:
        try:
            i0 = num.where(events.TIME >= tmin)[0][0]
            i1 = num.where(events.TIME <= tmax)[0][-1]
            imins.append(i0)
            imaxs.append(i1)
        except IndexError:
            # There are no events in this GTI, don't add the indices
            pass
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

class LogProbHist(object):
    def __init__(self, xmin=-200, xmax=0, nx=100):
        self.xmin = xmin
        self.xstep = (xmax - xmin)/float(nx)
        self.binValues = num.zeros(nx + 2)
    def add(self, xx):
        indx = int(xx - self.xmin)/self.xstep + 1
        if indx < 0:
            indx = 0
        elif indx > len(self.binValues) - 1:
            indx = len(self.binValues) - 1
        self.binValues[indx] += 1
    def xlims(self):
        return (num.arange(len(self.binValues) + 1)*self.xstep 
                + self.xmin - self.xstep)

class LogProbHists(object):
    def __init__(self, xmin=-200, xmax=0, nx=200):
        self.logdt = LogProbHist(xmin, xmax, nx)
        self.logdist = LogProbHist(xmin, xmax, nx)
        self.logProb = LogProbHist(xmin, xmax, nx)
    def add(self, logdt, logdist):
        self.logdt.add(logdt)
        self.logdist.add(logdist)
        self.logProb.add(logdt + logdist)
    def write(self, output):
        xlims = self.xlims()
        for tup in zip(xlims[:-1], xlims[1:], self.logdt.binValues, 
                       self.logdist.binValues, self.binValues):
            output.write("%12e  %12e  %12e  %12e  %12e\n" % tup)
    def __getattr__(self, attrname):
        return getattr(self.logProb, attrname)

def mkdir(new_dir):
    """Create a new directory and set permissions to be world-rwx-able"""
    try:
        os.mkdir(new_dir)
        os.chmod(new_dir, 0777)
    except OSError:
        # Directory may already exist.
        if os.path.isdir(new_dir):
            try:
                os.chmod(new_dir, 0777)
            except:
                pass
        else:
            raise OSError, "Error creating directory: " + new_dir

def apply_zmaxcut(infiles, ft2files, zmax=100):
    ft2Merged = 'FT2_merged.fits'
    tmpfile = 'filtered.fits'
    if ft2files:
        ft2merge(ft2files, ft2Merged)
    outfiles = []
    for infile in infiles:
        if ft2files:
            try:
                gtmktime.run(scfile=ft2Merged, filter='IN_SAA!=T && LIVETIME>0',
                             evfile=infile, outfile=tmpfile)
            except RuntimeError:
                # Probably encountered single 30 fragment for this run,
                # with incorrect start and stop times in corresponding FT2 file
                # filled by L1Proc.  Just pass it on unfiltered.
                tmpfile = infile
        else:
            tmpfile = infile
        outfile = infile.replace('.', '_zmax100.')
        outfile = os.path.basename(outfile)
        evclass = EventClassSelection(tmpfile)
        gtselect.run(infile=tmpfile, outfile=outfile, zmax=zmax, 
                     emin=0, emax=3e6, rad=180, evclass=evclass.transient)
        ft1 = pyfits.open(outfile)
        if ft1['EVENTS'].size != 0:
            outfiles.append(outfile)
        if ft2files:
            os.remove(tmpfile)
    return outfiles

def check_event_order(ft1_files):
    out_of_order = []
    for item in ft1_files:
        ft1 = FitsNTuple(item)
        dt = ft1.TIME[1:] - ft1.TIME[:-1]
        if min(dt) < 0:
            out_of_order.append(item)
    if out_of_order:
        message = "Out-of-order events found in \n"
        for item in out_of_order:
            message += item + "\n"
        raise ValueError(message)

def limb_approach(grb_id, ft2file='FT2_merged.fits', zmax=100):
    ft2 = pyfits.open(ft2file)
    col = lambda colname : ft2['SC_DATA'].data.field(colname)
    indx = num.where(grb_id > col('START'))[0][-1]
    zenangle = dist((col('RA_SCZ')[indx], col('DEC_SCZ')[indx]),
                    (col('RA_ZENITH')[indx], col('DEC_ZENITH')[indx]))
    return zenangle > zmax

if __name__ == '__main__':
    import sys
    from LatGcnNotice import LatGcnNotice
    from GrbAspConfig import grbAspConfig
    import grb_followup
    import dbAccess
    from getFitsData import filter_versions
    import grbASP
    from moveToXrootd import moveToXrootd

    grbASP.Event_enableFPE()
    
    grbroot_dir = os.path.abspath(os.environ['GRBROOTDIR'])

    fileStager = FileStager("GRB_blind_search/%s" % os.environ['DownlinkId'],
                            stageArea=grbroot_dir, cleanup=True,
                            messageLevel='CRITICAL')

    ft1_files = [x.strip().strip('+') for x in open('Ft1FileList')]
    print "staging FT1 files:"
    for item in ft1_files:
        print item
    downlink_files = fileStager.infiles(ft1_files)

    check_event_order(downlink_files)

    ft2_files = [x.strip().strip('+') for x in open('Ft2FileList')]
    print "staging FT2 files:"
    for item in ft2_files:
        print item
    ft2_files = fileStager.infiles(ft2_files)

    os.chdir(grbroot_dir)  # move to the working directory

    if not downlink_files:
        print "No FT1 files found. Exiting."
        sys.exit()

    #
    # Apply gtmktime and zenith_angle cut to each file, return only those 
    # filtered files with events remaining.
    # 
    zencut_files = apply_zmaxcut(downlink_files, ft2_files)

    if not zencut_files:
        print "No events pass zenith angle cut. Exiting."

        try:
            os.remove('FT2_merged.fits')
        except OSError:
            pass

        for item in zencut_files:
            os.remove(item)
        sys.exit()

    zencut_files.sort()
    raw_events = FitsNTuple(zencut_files)
    nMetStart = int(min(raw_events.TIME))
    nMetStop = int(max(raw_events.TIME))
    pipeline.setVariable('nMetStart', '%i' % nMetStart)
    pipeline.setVariable('nMetStop', '%i' % nMetStop)

    print "Number of events read: ", len(raw_events.TIME)
    print "from FT1 files: ", zencut_files

    gtis = read_gtis(zencut_files)
    clusterAlg = EventClusters(gtis)

    imins, imaxs = gti_bounds(raw_events, gtis)

    package = PackagedEvents(raw_events)

    times = num.array([])
    logdts = num.array([])
    logdists = num.array([])

    grb_candidates = []

    print imins, imaxs
    for imin, imax in zip(imins, imaxs):
        events = package(imin, imax)

        if len(events.TIME) > 0:
            try:
                grbConfig = grbAspConfig.find(min(events.TIME))
            except RuntimeError:
                grbConfig = grbAspConfig.find(618793145)
        if len(events.TIME) < 2:
            continue

        print "imin, imax = ", imin, imax
        print "# events = ", len(events.TIME)

        print "using threshold ", grbConfig.THRESHOLD

        blindSearch = BlindSearch(events, clusterAlg, 
                                  dn=grbConfig.PARTITIONSIZE,
                                  deadtime=grbConfig.DEADTIME, 
                                  threshold=grbConfig.THRESHOLD,
                                  bg_window=50)

        times = num.concatenate((times, blindSearch.times))
        logdts = num.concatenate((logdts, blindSearch.logdts))
        logdists = num.concatenate((logdists, blindSearch.logdists))

        grbDirs = blindSearch.grbDirs()
        grb_candidates.extend(grbDirs)

    filename = 'logProbs_%s.fits' % os.environ['DownlinkId']

    filepath = os.path.join(grbroot_dir, filename)
    print "writing ", filepath
    writeTimeHistory(times, logdts, logdists, filepath)

    try:
        figures = createPlots(filename, os.environ['DownlinkId'],
                              -grbConfig.THRESHOLD)
    except (NameError, FitsNTupleError):
        # if there are no events then grbConfig is not set, so skip
        # generating the figures, which are only used in the email
        # notifications
        figures = []
        pass

    for item in grb_candidates:
        grb_dir, tpeak, logProb = item
        print grb_dir.ra(), grb_dir.dec(), tpeak, logProb
        #
        # Use GCNNOTICES db table to keep track of GRBs found via
        # blind search.  This will likely occur after all other
        # instruments/missions (GBM, Swift) have already sent out
        # their GCN Notices, so the blind search result will
        # automatically be the position used in the refinement
        # task.  Need to sort out Notice type precedence for this.
        #
        # Do not write this Notice out, since the ASP Notice will
        # be generated after the GRB_refinement task.
        #
        notice = LatGcnNotice(tpeak, grb_dir.ra(), grb_dir.dec())
        #
        # Use default location error of 1 deg based on analyses 
        # of GRID 1 data:
        #
        notice.setLocErr(1.)
        #
        # Need better logic to check if this burst already has a
        # Notice from a different mission/instrument. Here we just
        # check that the grb_id (int(MET of burst)) hasn't already
        # been used by an entry in the GRB database table.
        #
        isUpdate = dbAccess.haveGrb(notice.grb_id)
#        #
#        # Check if this burst candidate occurs during nadirOps.  If
#        # so, skip it.
#        #
#        moot_alias = dbAccess.get_moot_alias(notice.grb_id)
#        print notice.grb_id, moot_alias
#        if moot_alias == 'nadirOps':
#            print 'GRB candidate %i acquired during nadirOps; skipping.' \
#                % notice.grb_id
#            continue
        #
        # Check if candidate occurs at outset of a limb transit/Earth 
        # avoidance maneuver
        #
        if limb_approach(notice.grb_id):
            print 'GRB candidate %i acquired during limb approach; skipping.' \
                % notice.grb_id
            continue
        #
        # Check if candidate is within 30 deg of Galactic Center during
        # modified GC survey mode for 2014:
        #
        if (dist((grb_dir.ra(), grb_dir.dec()), (266.40, -28.94)) < 30):
            print 'GRB candidate %i at (RA, Dec) = %.2f, %.2f within 30 deg of Galactic Center' % (notice.grb_id, grb_dir.ra(), grb_dir.dec())
            notice.email_notification(logProb, grbConfig.THRESHOLD,
                                      recipients=['jchiang@slac.stanford.edu'],
                                      files=ft1_files, figures=figures)
            continue
        #
        notice_type = None
        if isUpdate:
            sql = ("select NOTICETYPE from gcnnotices where grb_id=%i" 
                   % notice.grb_id)
            notice_type = dbAccess.apply(sql, lambda cur:[x[0] for x in cur])[0]
        #
        if notice_type != 'ASP_BLIND_SEARCH':
            if os.environ['PIPELINESERVER'] == 'PROD':
                notice.email_notification(logProb, grbConfig.THRESHOLD,
                                          files=ft1_files, figures=figures)
            else:
                notice.email_notification(logProb, grbConfig.THRESHOLD,
                                          recipients=['jchiang@slac.stanford.edu'],
                                          files=ft1_files, figures=figures)
#        notice.registerWithDatabase(isUpdate=isUpdate)
        grb_output = os.path.join(grbroot_dir, `notice.grb_id`)
        mkdir(grb_output)
        notice.setTriggerNum(tpeak)
        notice.addComment(', '.join(downlink_files))
        print grb_dir.ra(), grb_dir.dec(), tpeak
            
    try:
        os.remove('FT2_merged.fits')
    except OSError:
        pass

    for item in zencut_files:
        os.remove(item)

    for item in figures:
        os.remove(item)

    outfile_location = moveToXrootd(filepath, grbroot_dir)
    pipeline.setVariable('filepath', outfile_location)

    grb_followup.handle_unprocessed_events(grbroot_dir)
