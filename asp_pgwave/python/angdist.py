import string, os, math
DEG_RAD=math.pi/180

def angDistance(ra1,dec1,ra2,dec2):
	ra1 = ra1 *DEG_RAD;
	dec1 = dec1 * DEG_RAD;
	ra2 = ra2 *DEG_RAD;
	dec2 = dec2 * DEG_RAD;
	x1 = math.cos(ra1)*math.cos(dec1);
	y1 = math.sin(ra1)*math.cos(dec1);
	z1 = math.sin(dec1);
	x2 = math.cos(ra2)*math.cos(dec2);
	y2 = math.sin(ra2)*math.cos(dec2);
	z2 = math.sin(dec2);
	costheta =(x1*x2+y1*y2+z1*z2)
	return math.acos(costheta)/DEG_RAD
