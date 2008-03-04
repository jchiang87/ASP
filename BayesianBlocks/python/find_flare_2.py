import sys, os
sys.path.append('../python')
sys.path.append(os.path.join(os.environ['LIKEGUIROOT'], 'python'))
sys.path.append(os.path.join(os.environ['SANEROOT'], 'python'))
import numarray as num
import numarray.ma as ma
import celgal
import copy
from FitsNTuple import FitsNTuple
from xml.dom import minidom

from BayesBlocks import BayesBlocks, LightCurve
from BayesianBlocks import Exposure, DoubleVector

import string

def roiCenter(xmlFile):
    (src, ) = minidom.parse(xmlFile).getElementsByTagName('source')
    (dir, ) = src.getElementsByTagName('celestial_dir')
    ra = string.atof(dir.getAttribute('ra'))
    dec = string.atof(dir.getAttribute('dec'))
    return ra, dec

def get_times(data, Roi_center, radius=20):
    data.dist = celgal.dist(Roi_center, (data.RA, data.DEC))
    tmp = ma.masked_greater(data.dist, radius)
    times = ma.array(data.TIME, mask=tmp.mask())
    xx = [time for time in times.tolist() if time != times.fill_value()[0]]
    xx.sort()
    return xx

def effAreaScaleFactors(Roi_center, evt_times, npts=1000,
                        scData='eg_diffuse_scData_0000.fits'):
    block_times = (num.arange(npts, type=num.Float)/(npts-1)
                   *(evt_times[-1] - evt_times[0]) + evt_times[0])
    block_times = DoubleVector(block_times.tolist())
    my_exposure = Exposure(scData, block_times, Roi_center[0], Roi_center[1])
    EA_scaleFactors = []
    for t in evt_times:
        EA_scaleFactors.append(my_exposure.value(t))
    x = num.array(EA_scaleFactors)
    x *= (0.05/max(x))
    x += (max(x)/1e5)
    return DoubleVector(x.tolist())

def find_flare(flareFile, diffuseFile, roiFile='random_flare.xml',
               roiRadius=20.):
    flare = FitsNTuple(flareFile)
    diffuse = FitsNTuple(diffuseFile)
    Roi_center = roiCenter('random_flare.xml')

    flare_times = get_times(flare, Roi_center, radius=roiRadius)
    diffuse_times = get_times(diffuse, Roi_center, radius=roiRadius)

    evt_times = flare_times + diffuse_times
    evt_times.sort()
    #
    # diffuse event scaling
    #
    diffuse_only = BayesBlocks(diffuse_times)
    diffuse_only_lc = LightCurve(diffuse_only.computeLightCurve())
    scaleFactors = diffuse_only_lc(evt_times)
    flare_blocks = BayesBlocks(evt_times, 4)
    flare_blocks.setCellScaling(scaleFactors)
    #
    # effective area scaling
    #
    EA_scaleFactors = effAreaScaleFactors(Roi_center, evt_times)
    flare_blocks_ea = BayesBlocks(evt_times, 4)
    flare_blocks_ea.setCellScaling(EA_scaleFactors)

    return (evt_times, flare_times, flare_blocks.computeLightCurve(),
            flare_blocks_ea.computeLightCurve())

def first_rise(blockData, start=1):
    for i in range(start, len(blockData[0])):
        if blockData[2][i] > blockData[2][i-1]:
            return blockData[0][i]
    return blockData[0][0]

if __name__ == "__main__":
    (evt_times, flare_times, flare_blocks,
     flare_blocks_ea) = find_flare("random_flare_events_0000.fits",
                                   "eg_diffuse_events_0000.fits")
    import hippoplotter as plot
    hist = plot.histogram(evt_times)#, ylog=1)
    hist.setLabel('x', 'Time (s)')
    plot.histogram(flare_times, oplot=1, color='red', autoscale=1)
    plot.canvas.selectDisplay(hist)
    flare_lc = LightCurve(flare_blocks).dataPoints()
    plot.scatter(flare_lc[0], flare_lc[1], oplot=1, color='green',
                 pointRep='Line', autoscale=1)
    flare_onset = first_rise(flare_blocks)
    
    flare_lc_ea = LightCurve(flare_blocks_ea).dataPoints()
    plot.scatter(flare_lc_ea[0], flare_lc_ea[1], oplot=1, color='green',
                 pointRep='Line', lineStyle='Dot', autoscale=1)
    flare_onset_ea = first_rise(flare_blocks_ea)

    import time
    time.sleep(0.1)
    plot.vline(flare_onset)
    plot.vline(flare_onset_ea)
