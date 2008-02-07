def sexigesimal(ra, dec):
    degperhr = 360/24
    ra_hours = int(ra/degperhr)
    ra_mins = int((ra - ra_hours*degperhr)/degperhr*60.)
    ra_secs = int((ra - ra_hours*degperhr -ra_mins/60.*degperhr)/degperhr*3600)

    sign = 1
    if dec < 0:
        sign = -1
        dec *= -1
        
    dec_degs = int(dec)
    dec_mins = int((dec - dec_degs)*60)
    frac = dec - dec_degs - dec_mins/60.
    dec_secs = int(frac*3600)
    if sign == 1:
        return ("+%02ih %02im %02is" % (ra_hours, ra_mins, ra_secs),
                "+%02id %02i' %02i\"" % (dec_degs, dec_mins, dec_secs))
    else:
        return ("+%02ih %02im %02is" % (ra_hours, ra_mins, ra_secs),
                "-%02id %02i' %02i\"" % (dec_degs, dec_mins, dec_secs))

if __name__ == '__main__':
    print "%s  %s" % sexigesimal(193.98, -5.82)
    
    
