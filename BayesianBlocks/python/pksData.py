import sys
sys.path.reverse()
sys.path.append('/scratch/jchiang/HippoDev/hippodraw/python')
sys.path.append('/home/jchiang/ST/likeGui/v6/python')
sys.path.reverse()
import numpy as num
import hippoplotter as plot
import glob

galdiffuse = plot.FitsNTuple(glob.glob('GalDiffuse_6.6days_events_*.fits'))
diffuse = plot.FitsNTuple('eg_diffuse_6.6days_events_0000.fits')
pks1622 = plot.FitsNTuple('pks1622-297_events_0000.fits')

from celgal import celgal, dist

srcPos = (246.36, -29.92)
def add_separations(data, srcPos):
    my_dists = dist((data[1].RA, data[1].DEC), srcPos)
    data[0].addColumn('distance', my_dists)

add_separations(galdiffuse, srcPos)
add_separations(diffuse, srcPos)
add_separations(pks1622, srcPos)

