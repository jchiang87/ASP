"""
@brief Ingest all of the files that were archived by the
GCN_Notice_processor.py.

@author J. Chiang
"""
#
# $Header$
#

import os
import subprocess
import sys
import glob
import smtplib
import numpy as np
from ingestEmailNotice import Packet, registerWithDatabase
from GCN_Notice_processor import GcnNoticeEmail
from PipelineCommand import resolve_nfs_path
from GBM_Notice_parser import GBM_Notice_parser

def forwardErrorMessage(msg):
    preamble = ("Subject: ingestNoticeQueue error\n" +
                "Exception raised in processing the GCN email text:\n")
    mail = smtplib.SMTP('smtpunix.slac.stanford.edu')
    fromaddr = 'glastgcn@slac.stanford.edu'
    toaddr = 'jchiang@slac.stanford.edu'
    mail.sendmail(fromaddr, toaddr, "%s%s" % (preamble, msg))
    mail.quit()

def Angdist(x):
    """Angular distance in radians corresponding to a cosinus""" 
    if np.abs(x) < 1:
        angdist = np.arccos(x)
    elif np.abs(x) < 1.00001:
        angdist = np.pi/2.*(1 - int(x))
    else:
        raise ValueError, "x must be smaller than 1"
    return angdist

def dist(a, b):
    """Angular separation in degrees between two sky coordinates"""
    ra1, dec1 = a
    ra2, dec2 = b
    ra1 = ra1*np.pi/180.
    dec1 = dec1*np.pi/180.
    ra2 = ra2*np.pi/180.
    dec2 = dec2*np.pi/180.
    mu = (np.cos(dec1)*np.cos(ra1)*np.cos(dec2)*np.cos(ra2)
          + np.cos(dec1)*np.sin(ra1)*np.cos(dec2)*np.sin(ra2) 
          + np.sin(dec1)*np.sin(dec2))
    return Angdist(mu)*180./np.pi

def skip(packet):
    V404_Cygni = (306.0159, 33.8673)
    angsep = dist(V404_Cygni, (packet.RA, packet.Dec))
    if ((packet.mission == 'FERMI' and angsep < 20) or 
        (packet.mission == 'INTEGRAL' and angsep < 1)):
        return True
    return False

#archive_path = "/nfs/farm/g/glast/u52/ASP/GCN_Archive"
archive_path = "/nfs/farm/g/glast/u41/ASP/GCN_Archive"
#archive_path = "/afs/slac/g/glast/ground/links/data/ASP/GCN_Archive"

if sys.argv[1:]:
    os.chdir(sys.argv[1])
else:
    os.chdir(os.path.join(archive_path, "NOTICE_QUEUE"))

notices = glob.glob('tmp*')

skipped_notice_types = ('SWIFT_SC_SLEW', 'SWIFT_UVOT_POSITION_NACK',
                        'INTEGRAL_WAKEUP', 'INTEGRAL_REFINED')

for notice in notices:
    try:
        packet = Packet(notice)
#        if skip(packet):
#            continue
        #
        # Fill FERMI_GCN_NOTICE_INFO table
        #
        try:
            gbm_parser = GBM_Notice_parser(open(notice))
            gbm_parser.update_tables()
        except:
            pass
        #
        # Fill GCNNOTICES table
        #
        if ((packet.trigger_num==99999 and packet.mission.lower()=='fermi') or
            (packet.notice_type in skipped_notice_types)):
            pass
        else:
            my_notice = GcnNoticeEmail(open(notice).readlines())
            outfile = my_notice.writeArchive(archive_path)
#            registerWithDatabase(packet, resolve_nfs_path(outfile))
        #
        # clean-up tmp file if all is successful.
        #
        os.remove(notice)
    except Exception, msg:
        os.rename(notice, "_" + notice)
        message = str(msg) + ("\nfor notice file %s" % notice)
        forwardErrorMessage(message)

#try:
#    command = "/afs/slac/g/glast/groups/grb/Weekly_FT2/GCN_off_axis_plots/plot_offaxis_angles.sh"
#    subprocess.call(command, shell=True)
#except Exception, msg:
#    forwardErrorMessage(msg)
