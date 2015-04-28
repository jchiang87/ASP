import os
#os.system('source ../cmt/setup.csh')

import sys
sys.path.append('../python')
sys.path.append(os.path.join(os.environ['LIKEGUIROOT'], 'python'))
sys.path.append(os.path.join(os.environ['SANEROOT'], 'python'))

from pil import Pil

from xml.dom import minidom
import random
import numpy as num

def randomSkyDir():
    ra = random.random()*360.
    mu = random.random()*2. - 1.
    colat = num.arccos(mu)
    dec = (num.pi/2. - colat)*180./num.pi
    return ra, dec

def randomFlare(window=(0, 8.64e4), file='random_flare.xml',
                duration=4.32e4, flux=10., gamma=2., emin=30, emax=2e5):
    """
    Produce a hat-box flare at a random point on the sky,
    constrained to start within the given observing window.
    """
    src = '\n'.join( ('<source name="random_flare">', 
                      '   <spectrum escale="MeV">',
                      '      <SpectrumClass name="SimpleTransient"',
                      '       params="10., 2., 1e3, 1.1e3, 30., 2e5"/>',
                      '      <celestial_dir ra="246.36" dec="-29.92"/>',
                      '   </spectrum>',
                      '</source>') )
    (src, ) = minidom.parseString(src).getElementsByTagName('source')
    
    tstart = random.uniform(window[0], window[1])
    tstop = tstart + duration

    params = ("%.2e, "*5 + "%.2e") % (flux, gamma, tstart, tstop, emin, emax)
    (spectrumClass, ) = src.getElementsByTagName("SpectrumClass")
    spectrumClass.setAttribute('params', params)

    ra, dec = randomSkyDir()

    (celestial_dir, ) = src.getElementsByTagName('celestial_dir')
    celestial_dir.setAttribute('ra', '%.2f' % ra)
    celestial_dir.setAttribute('dec', '%.2f' % dec)

    return src, tstart

def writeXml(src, filename):
    file = open(filename, 'w')
    file.write('<source_library>\n')
    file.write(src.toxml().encode() + '\n')
    file.write('</source_library>\n')
    file.close()

obsSim = os.path.join(os.environ['OBSERVATIONSIMROOT'],
                      os.environ['BINDIR'], 'obsSim.exe')

def runObsSim(filename, file_prefix):
    pars = Pil('obsSim.par')
    pars['Source_list'] = 'random_source.dat'
    pars['Output_file_prefix'] = file_prefix
    pars['XML_source_file'] = filename
    pars['Start_time'] = 0
    pars['Number_of_events'] = 8.64e4*2
    command = ' '.join((obsSim, pars()))
    print command
    os.system(command)

if __name__ == '__main__':
    (src, tstart) = randomFlare(flux=0.1, window=(0, 2*8.64e4))
    xmlFile = 'random_flare.xml'
    writeXml(src, xmlFile)
    runObsSim(xmlFile, 'random_flare')
