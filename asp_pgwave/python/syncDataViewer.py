"""
@file syncDataViewer.py
@brief Poke the specified URL to synchronize the ASPDataViewer with
the recently inserted point sources.

@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import httplib

def syncDataViewer():
    conn = httplib.HTTPConnection('glast-ground.slac.stanford.edu')
    conn.request('GET', "/ASPDataViewer/synchronizeDataInfo")

    r = conn.getresponse()
    print r.status, r.reason
    print r.read()
    
    conn.close()
