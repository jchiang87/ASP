SIMPLE  = T                        / file does conform to FITS standard
BITPIX  = 8                        / number of bits per data pixel
NAXIS   = 0                        / number of data axes
EXTEND  = T                        / FITS dataset may contain extensions
CHECKSUM=                          / checksum for entire HDU
TELESCOP= 'GLAST'                  / name of telescope generating data
INSTRUME= 'LAT'                    / name of instrument generating data
EQUINOX = 2000.0                   / equinox for ra and dec
RADECSYS= 'FK5'                    / world coord. system (FK5 or FK4)
DATE    = '20??-??-?? ??:??:??'    / file creation date (UTC)
TIMEUNIT= 's'                      / units for the time related keywords
TIMESYS = 'TT'                     / type of time system that is used
GPS_OUT = F                        / whether GPS time was unavailable
MJDREFI = 51910.0                  / Int. part of MJD of SC clock start
MJDREFF =     7.428703703703703D-4 / Frac. part of MJD of SC clock start
OBSERVER= 'Peter Michelson'        / LAT PI
FILENAME= '???????????????' / name of this file:
ORIGIN  = 'LISOC'                  / name of organization making file
CREATOR =                          / software and version creating file
VERSION = 1                        / release version of the file
END

XTENSION= 'BINTABLE'           / binary table extension
BITPIX  =                    8 / array data type
NAXIS   =                    2 / number of array dimensions
NAXIS1  =                   98 / length of dimension 1
NAXIS2  =                  940 / length of dimension 2
PCOUNT  =                    0 / number of group parameters
GCOUNT  =                    1 / number of groups
TFIELDS =                   23 / number of table fields
COMMENT  
COMMENT  Added Units for relevant quantities
COMMENT  Added timing keywords
COMMENT  Tried to make it similar to 3rd EGRET src catalog where possible:
COMMENT      SOURCE -> NAME
COMMENT  Added Duration Column (STOP-START)
COMMENT
COMMENT  Some Questions:
COMMENT  what are flux errors? presumably 1-sigma? 
COMMENT  should we give some type of likelihood statistic (e.g. for the 
COMMENT    full energy + time interval?) 
COMMENT  
COMMENT  
COMMENT
COMMENT
TELESCOP= 'GLAST'                  / name of telescope generating data
INSTRUME= 'LAT'                    / name of instrument generating data
EQUINOX = 2000.0                   / equinox for ra and dec
RADECSYS= 'FK5'                    / world coord. system (FK5 or FK4)
DATE    = '20??-??-?? ??:??:??'    / file creation date (UTC)
TIMEUNIT= 's'                      / units for the time related keywords
TIMESYS = 'TT'                     / type of time system that is used
GPS_OUT = F                        / whether GPS time was unavailable
MJDREFI = 51910.0                  / Int. part of MJD of SC clock start
MJDREFF =     7.428703703703703D-4 / Frac. part of MJD of SC clock start
OBSERVER= 'Peter Michelson'        / LAT PI name 
ORIGIN  = 'LISOC'                  / name of organization making file
CREATOR =                          / software and version creating file
VERSION = 1                        / release version of the file
EXTNAME = 'LIGHTCURVES'            / extension name
TTYPE1  = 'START   '               / start time of interval in MET
TFORM1  = 'D       '
TUNIT1  = 'S       '               / Unit of time
TTYPE2  = 'STOP    '               / stop time of interval in MET
TFORM2  = 'D       '
TUNIT2  = 'S       '               / Unit of time
TTYPE3  = 'NAME    '               / LAT source name
TFORM3  = '30A     '
TTYPE4  = 'RA      '               / RA
TFORM4  = 'E       '
TUNIT4  = 'DEGREES '               / Unit of RIGHT ASCENSION
TTYPE5  = 'DEC     '               / Dec
TFORM5  = 'E       '
TUNIT5  = 'DEGREES '               / Unit of DECLINATION
#TTYPE6  = 'FLUX_100_3000'           / Flux, 100-3000 Mev
#TFORM6  = 'E       '
#TTYPE7  = 'ERROR_100_3000'          / 1-sigma error on flux
#TFORM7  = 'E       '
#TTYPE8  = 'UL_100_300'             / Flag to indicate flux value is a 90% CL UL
#TFORM8  = 'L       '
#TTYPE9  = 'FLUX_300_1000'          / Flux, 300-1000 MeV
#TFORM9  = 'E       '
#TTYPE10 = 'ERROR_300_1000'         / 1-sigma error on flux
#TFORM10 = 'E       '
#TTYPE11 = 'UL_300_1000'            / Flag to indicate flux value is a 90% CL UL
#TFORM11 = 'L       '
#TTYPE12 = 'FLUX_1000_3000'         / Flux, 1000-3000 MeV
#TFORM12 = 'E       '
#TTYPE13 = 'ERROR_1000_3000'        / 1-sigma error on flux 
#TFORM13 = 'E       '
#TTYPE14 = 'UL_1000_3000'           / Flag to indicate flux value is a 90% CL UL
#TFORM14 = 'L       '
#TTYPE15 = 'FLUX_3000_10000'        / Flux, 1000-3000 MeV
#TFORM15 = 'E       '
#TTYPE16 = 'ERROR_3000_10000'       / 1-sigma error on flux 
#TFORM16 = 'E       '
#TTYPE17 = 'UL_3000_10000'          / Flag to indicate flux value is a 90% CL UL
#TFORM17 = 'L       '
#TTYPE18 = 'FLUX_10000_300000'      / Flux, 10000-300000 MeV
#TFORM18 = 'E       '
#TTYPE19 = 'ERROR_10000_300000'     / 1-sigma error on flux 
#TFORM19 = 'E       '
#TTYPE20 = 'UL_10000_300000'        / Flag to indicate flux value is a 90% CL UL
#TFORM20 = 'L       '
#TTYPE21 = 'FLUX_100_300000'        / Flux 100-30000 MeV
#TFORM21 = 'E       '
#TTYPE22 = 'ERROR_100_300000'       / 1-sigma error on flux 
#TFORM22 = 'E       '
#TTYPE23 = 'UL_100_300000'          / Flag to indicate flux value is a 90% CL UL
#TFORM23 = 'L       '
#TTYPE24 = 'DURATION'               / time interval duration: stop - start
#TFORM24 = 'E       '
#TUNIT24 = 'S        '              / Unit of duration
#TTYPE25 = 'TEST_STATISTIC'         / Test statistic for 100-300000 MeV measurement
#TFORM25 = 'E       '
#TTYPE26 = 'ALT NAME 1             / Alternative source name (Source Name in LAT monitored source list)
#TFORM26 = '20A     '
#TTYPE27 = 'ALT NAME 2    '        / Alternative source name 2 (3EG)
#TFORM27 = '20A     '
#TTYPE4  = 'RA_SRC  '              / RA of catalogued source
#TFORM4  = 'E       '
#TUNIT4  = 'DEGREES '              / Unit of RIGHT ASCENSION
#TTYPE5  = 'DEC_SRC '              / Dec of catalogued source
#TFORM5  = 'E       '
#TUNIT5  = 'DEGREES '              / Unit of DECLINATION
#TTYPE5  = 'Separation  '          / separation bet. catalogued source and LAT source
#TFORM5  = 'E       '
#TUNIT5  = 'DEGREES '              / Unit of separation
HISTORY
HISTORY
HISTORY  give processing tools and parameters here (if possible)
HISTORY 
HISTORY
END
