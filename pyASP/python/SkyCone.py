"""
@brief Utilities to compute and plot acceptance cones in Celestial
coordinates
@author J. Chiang <jchiang@slac.stanford.edu>
"""
#
# $Header$
#

import copy

import numarray as num
from numarray import pi, cos, sin, arcsin, arctan2

import hippoplotter as plot
import celgal

na = num.array
convertTo = celgal.celgal()

class SkyDir(object):
    def __init__(self, ra=0, dec=0, coordsys='CEL', spin=1):
        self.spin = spin
        if coordsys != 'CEL': # assume Galactic
            ra, dec = convertTo.cel((ra, dec))
        ra *= pi/180.
        dec *= pi/180.
        self.unit = num.array([cos(dec)*cos(ra),
                               cos(dec)*sin(ra),
                               sin(dec)])
    def rotate(self, axis, angle):
        rot = Rotation()
        rot.rotate(axis, angle)
        self.unit = rot*self.unit
    def ra(self):
        my_ra = arctan2(self.unit[1], self.unit[0])*180./pi
        if self.spin:
            if my_ra < 0: my_ra += 360.
        return my_ra
    def dec(self):
        return arcsin(self.unit[2])*180./pi
    def l(self):
        return convertTo.glon(self.ra(), self.dec())
    def b(self):
        return convertTo.glat(self.ra(), self.dec())
    def separation(self, skyDir):
        return celgal.dist((self.ra(), self.dec()),
                           (skyDir.ra(), skyDir.dec()))

class Rotation(object):
    def __init__(self, matrix=None):
        if matrix is None:
            self.matrix = num.array([[1, 0, 0],
                                     [0, 1, 0],
                                     [0, 0, 1]])
        else:
            self.matrix = copy.deepcopy(matrix)
    def rotate(self, axis, angle):
        theta = angle*pi/180.
        ct = cos(theta)
        st = sin(theta)
        if axis.lower() == 'x':
            A = num.array([[1,  0,   0],
                           [0, ct, -st],
                           [0, st,  ct]])
        elif axis.lower() == 'y':
            A = num.array([[ ct, 0, st],
                           [  0, 1,  0],
                           [-st, 0, ct]])
        elif axis.lower() == 'z':
            A = num.array([[ct, -st, 0],
                           [st,  ct, 0],
                           [ 0,   0, 1]])
        self.matrix = num.matrixmultiply(A, self.matrix)
        return self
    def inverse(self):
        a = copy.deepcopy(self.matrix)
        a.transpose()
        return Rotation(a)
    def __mul__(self, rhs):
        if isinstance(rhs, Rotation):
            result = num.matrixmultiply(self.matrix, rhs.matrix)
            return Rotation(result)
        else:
            result = num.matrixmultiply(self.matrix, rhs)
            return result
    def __rmul__(self, lhs):
        if isinstance(lhs, Rotation):
            result = num.matrixmultiply(lhs.matrix, self.matrix)
            return Rotation(result)
        else:
            result = num.matrixmultiply(lhs, self.matrix)
            return result
    def __repr__(self):
        return `self.matrix`

def makeCone(ra, dec, radius, npts = 50):
    center = SkyDir(ra, dec)
    #
    # Rotate center to align with z-axis.
    #
    rot = Rotation().rotate('z', -ra).rotate('y', dec-90.)
    rotatedCenter = rot*center.unit
    inv = rot.inverse()
    #
    # Create the acceptance cone about z-axis and rotate back.
    #
    phis = num.arange(npts)/float(npts-1)*360.
    ra_vals = []
    dec_vals = []
    coneDir = SkyDir()
    for phi in phis:
        coneDir.unit = inv*SkyDir(phi, 90. - radius).unit
        ra_vals.append(coneDir.ra())
        dec_vals.append(coneDir.dec())
    return num.array(ra_vals), num.array(dec_vals)

def plotCone(disp, pos=(0, 0), radius=20, color='red', connect=0,
             oplot=1):
    ras, decs = makeCone(pos[0], pos[1], radius)
    plot.canvas.selectDisplay(disp)
    if connect:
        return plot.scatter(ras, decs, pointRep='Line', color=color,
                            oplot=oplot)
    else:
        return plot.scatter(ras, decs, color=color, oplot=oplot)

if __name__ == "__main__":
    import hippoplotter as plot
    ras, decs = makeCone(83, 22, 20)
    my_map = plot.scatter(ras, decs, 'ra', 'dec',
                          xrange=(-180, 180), yrange=(-90, 90),
                          pointRep='Line')
    for dec in (50, 60, 70, 80):
        print dec
        plotCone(my_map, (90, dec))
        plot.prompt()
        
    
