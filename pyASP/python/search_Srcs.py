#!/usr/bin/env python
#
# PURPOSE: Search in the XML sources lists 
#
# ALGORITHM: Build a structure table TSrcs
#         containing fields values for each
#         source.
#            Build a search expression, with
#         known attributes and known elements
#         from the table.
#            Apply the search to each element.
#            Display the results
#
#
##############################################
#
# $Header$
#

import sys,re,os

from xml.dom import minidom

####### Insert celgal.py to keep the tool search_Srcs.py autonomous #####
"""
Class for transforming between Equatorial and Galactic coordinates.

@author J. Chiang <jchiang@slac.stanford.edu>

"""

try:
    from numarray import *
except ImportError:
    from math import *
    arcsin = asin
    arccos = acos
    arctan2 = atan2

class celgal:
    def __init__(self, J2000=1):
        #
        # Rotation angles for the two most common epochs
        #
        if J2000:
            self.zrot1 = 282.8592
            self.xrot = 62.8717
            self.zrot2 = 32.93224
        else: # use B1950 values
            self.zrot1 = 282.25
            self.xrot = 62.6
            self.zrot2 = 33.

        self.cos_xrot = cos(self.xrot*pi/180.)
        self.sin_xrot = sin(self.xrot*pi/180.)

    def gal(self, radec):
        (ra, dec) = radec
        return (self.glon(ra, dec), self.glat(ra, dec))

    def cel(self, lb):
        (glon, glat) = lb
        return (self.RA(glon, glat), self.DEC(glon, glat))

    def glon(self, ra, dec) :
        """Galactic longitude as a function of Equatorial coordinates"""
        sdec = sin(dec*pi/180.)
        cdec = cos(dec*pi/180.)
        sdra = sin((ra-self.zrot1)*pi/180.)
        cdra = cos((ra-self.zrot1)*pi/180.)
        glon = self.zrot2 + arctan2(cdec*sdra*self.cos_xrot+sdec*self.sin_xrot,
                                    cdec*cdra)*180./pi
        try:
            if glon < 0. : glon += 360.
            if glon > 360. : glon -= 360.
        except RuntimeError:
            for i in xrange(len(glon)):
                if glon[i] < 0.: glon[i] += 360.
                if glon[i] > 360.: glon[i] -= 360.
        return glon

    def glat(self, ra, dec) :
        """Galactic latitude as a function of Equatorial coordinates"""
        sdec = sin(dec*pi/180.)
        cdec = cos(dec*pi/180.)
        sdra = sin((ra-self.zrot1)*pi/180.)
        return arcsin(sdec*self.cos_xrot-cdec*sdra*self.sin_xrot)*180./pi
            
    def RA(self, longitude, latitude) :
        """Right ascension as a function of Galactic coordinates"""
        clat = cos(latitude*pi/180.)
        slat = sin(latitude*pi/180.)
        cdlon = cos((longitude-self.zrot2)*pi/180.)
        sdlon = sin((longitude-self.zrot2)*pi/180.)
        ra = self.zrot1 + arctan2(clat*sdlon*self.cos_xrot-slat*self.sin_xrot,
                                  clat*cdlon)*180./pi
        try:
            if ra < 0. : ra = ra + 360.
            if ra > 360. : ra = ra - 360.
        except RuntimeError:
            for i in xrange(len(ra)):
                if ra[i] < 0.: ra[i] += 360.
                if ra[i] > 360.: ra[i] -= 360.
        return ra

    def DEC(self, longitude, latitude) :
        """Declination as a function of Galactic coordinates"""
        clat = cos(latitude*pi/180.)
        slat = sin(latitude*pi/180.)
        sdlon = sin((longitude-self.zrot2)*pi/180.)
        return arcsin(clat*sdlon*self.sin_xrot+slat*self.cos_xrot)*180./pi
    
def dist( a, b ):
    """Angular separation in degrees between two sky coordinates"""
    (ra1, dec1) = a
    (ra2, dec2) = b
    ra1 = ra1*pi/180.
    dec1 = dec1*pi/180.
    ra2 = ra2*pi/180.
    dec2 = dec2*pi/180.
    mu = (cos(dec1)*cos(ra1)*cos(dec2)*cos(ra2)
          + cos(dec1)*sin(ra1)*cos(dec2)*sin(ra2) + sin(dec1)*sin(dec2))
    return Angdist(mu)*180./pi

def SphCoords(u):
   """ Spherical coordinates in radians for a normalised 3Dvector u """     
   if abs(u[2])< 1 :
      theta_rad = math.asin(u[2])
      if abs(u[0])>.00001:     
         phi_rad = math.atan(u[1]/u[0])+pi*(1-u[0]/abs(u[0]))/2.
      else:
         phi_rad = ( pi /2. - u[1]/cos(theta_rad)) * u[1]/abs(u[1])  
   else:
      theta_rad = pi /2. * int(u[2])
      phi_rad = 0  

   return(phi_rad,theta_rad)

def Angdist(x):
   """ Angular distance in radians corresponding to a cosinus  """ 
   if abs(x) < 1:
      angdist = arccos(x)
   elif abs(x) < 1.00001:
      angdist = pi/2 * (1-int(x))
   else:   
      print "Error: x must be smaller than 1"

   return angdist

### Define functions glon and glat from celgal methods:
def glon(ra, dec) :
  return celgal().glon(ra,dec)
    
def glat(ra, dec) :
  return celgal().glat(ra,dec)
    
####################################################
def union(a,b):
  c = []
  for x in a+b:
    if x not in c:
      c.append(x)  
  return c

####################################################
# Build the TSrcs structures table from XML file
def parseXMLModel(srcModel):
  
# XML object 'source' has attributes and elements :
  known_attributes = {}
  known_elements = {}

  doc1 = minidom.parse(srcModel)

  srcs = doc1.getElementsByTagName('source')

  srcnames = []
  indices = []
  Tsrcs = []

  isrc = 0
  
  for src in srcs:

    Tsrc = {}
    Tatts = []
    Telems = []
    
#   Get attributes with typed values :
    tpars = src.attributes.keys()

    for tpar in tpars:

      if tpar not in known_attributes:
        Tatts.append(tpar)
        
      Tsrc[tpar] = src.getAttribute(tpar).encode('ascii')
           
      if re.match(r"^-?\d*$", Tsrc[tpar]) and tpar!='name':
        Tsrc[tpar] = int( Tsrc[tpar] )
      elif re.match(r"^-?[\d?]*\.?[\d?]*[eE]?-?[\d?]*$",\
                  Tsrc[tpar]) and tpar!='name':
        Tsrc[tpar] = float( Tsrc[tpar] )

    elems = src.getElementsByTagName('*')

#   Get elements with typed values :
    Enames = []
    for oelem in elems: 

      ElementName = oelem.getAttribute('name').encode('ascii')
      Enames.append(ElementName)      

      elem_keys = oelem.attributes.keys()
      
      for elem_key in elem_keys:
          
        field_name = elem_key+"("+ElementName+")"
        
        if field_name not in known_elements and field_name != "":
          Telems.append(field_name)

        Tsrc[field_name] = oelem.getAttribute(elem_key).encode('ascii')
        if re.match(r"^-?\d*$", Tsrc[field_name]) and field_name != 'name':
          Tsrc[field_name] = int( Tsrc[field_name] )
        elif re.match(r"^-?[\d?]*\.?[\d?]*[eE]?-?[\d?]*$",\
                    Tsrc[field_name]) and field_name != 'name':
          Tsrc[field_name] = float( Tsrc[field_name] )

##        print "Tsrc[",field_name,"]",Tsrc[field_name],type(Tsrc[field_name])

    Tsrcs.append(Tsrc)
    known_attributes[isrc] = Tatts
    known_elements[isrc] = Telems
    isrc += 1
   
  return srcs,Tsrcs,Enames,known_attributes,known_elements

##############################################################
def Build_expression( expression, Enames, known_attributes,
                      known_elements):

  found_attributes = []

  for attr in known_attributes:
     if re.match( r"(.*)("+attr+")(.*)",expression):
       found_attributes.append(attr) 
       expression = re.sub( r"("+attr+")",
                          r"Tsrcs[isrc]['\1']",expression)
       
#   First scan of expression to build an expression without
#   known elements and keeping information in table TK :
  TK=[]
  ik=0
  for elem in known_elements:
    TK.append(elem)
    exec "TK"+str(ik)+"K = TK[ik]"
#   
  EXP = expression
  for elem in known_elements:
   
    elemp = re.sub(r"\(",r"\(",elem)
    elemp = re.sub(r"\)",r"\)",elemp)

    replacement_string = "TK"+str(TK.index(elem))+"K"  
    EXP = re.sub( elemp,replacement_string,EXP)

# Allow use of shortcut in expression request: RA instead of value(RA) ...
  while "" in Enames:
    Enames.remove("")
  
  for elem in Enames:
    ss = "(.*\s?)("+elem+")(.*)"
    if re.match( r""+ss,EXP):
      EXP = re.sub( elem,"value("+elem+")",EXP)

# Do now the last replacement:
  while re.match(r".*TK\d*K",EXP):
    tk = re.sub(r".*(TK\d*K).*",r"\1",EXP)
    itk = int(re.sub(r"TK(\d*)K",r"\1",tk))
    EXP = re.sub(tk,TK[itk],EXP)

  return EXP,found_attributes

######################################
# Build the search expression in TSrcs for each source
# And Apply it :
def search_Srcs(srcModel,expression,output_srcs_list):

  original_expression = expression

  srcs,Tsrcs,Enames,known_attributes,known_elements = \
                    parseXMLModel(srcModel)

  union_attributs = [] 
  for akey in known_attributes.keys():
    union_attributs = union(union_attributs,known_attributes[akey])
  for akey in known_elements.keys():
    union_attributs = union(union_attributs,known_elements[akey])
  
  union_attributs = union(union_attributs,Enames)
  
  if expression == "":
    print "Empty expression.\n"
    print "known attributes/elements:",union_attributs,"\n"
    print

    return
#
  attributs_exp = re.split(r"\W",expression)
  for att in attributs_exp:
    if att not in union_attributs or \
       att == '':
      attributs_exp.remove(att)
#
  found_one = False
  result_srclist = []

  for isrc in range(0,len(Tsrcs)):

    Tsrc = Tsrcs[isrc] 
          
    EXP , found_attributes = Build_expression(
                      expression,
                      Enames,                       
                      known_attributes[isrc],
                      known_elements[isrc] )

#   Look if source has one the expression descriptor:
    NoAttributInExpression= True
    for att in attributs_exp:
      union_atts = union(known_attributes[isrc],known_elements[isrc])
      if att in Enames:
        value_att = 'value('+att+')'  
        if value_att in union_atts:
          NoAttributInExpression = False  

    if NoAttributInExpression:
      continue  
       
    found_elements = []
    for elem in known_elements[isrc]:
      elemp = re.sub(r"\(",r"\(",elem)
      elemp = re.sub(r"\)",r"\)",elemp)
      if re.match(r".*"+elemp,EXP):
        found_elements.append(elem)
      
      EXP = re.sub( elemp,
                "Tsrcs[isrc]['"+elem+"']",EXP)
##      print ">>> EXP:",EXP
##      print  "found_elements:",found_elements

#   Quick fix of the case attribute = name
    found_attributes.reverse()

    try: 
      exec "found ="+EXP
    except AttributeError: 
      print "Expression error:",EXP,":AttributeError\n"
      print "Known attributes:",union_attributs,"\n"
      return
    except NameError: 
      print "Expression error:",EXP,":NameError\n"
      print "Known attributes:",union_attributs,"\n"
      return
    except TypeError: 
      print "Expression error:",EXP,":TypeError\n"
      return
    except KeyError:
      print "Expression error:",EXP,":KeyError\n"
      print Tsrc['name']
      found = False
      
    if found:
      if not found_one:
        print "Results from the request:",original_expression
        print "-------------------------"
      found_one = True
      txt = ""
      if 'name' not in found_attributes:
        txt = "'"+Tsrc['name']+":'"
        
      for item in found_attributes:
        txt += ",'"+item+":',Tsrc['"+item+"']"

      for item in found_elements:
        txt += ",'"+item+":',"+str(Tsrc[item])

      txt = re.sub(r"^,(.*)$",r"\1",txt)

      exec "print "+txt

#     Fill output :
      result_srclist.append(srcs[isrc])
      
  if not found_one:
    print "No source matches the given criteria:"
    print "original_expression:",original_expression
    print "expression:",expression
  else:
    f = open(output_srcs_list, 'w')

    f.write('<?xml version="1.0" ?>'+"\n")
    f.write("<!--- Result from request: "+\
            original_expression+" -->\n" )
    f.write("<!--- In file: "+srcModel+" -->\n")
            
    f.write("<source_library title=\"source library\">\n")

    for src in result_srclist:
   
      lines = re.split("\n",src.toxml())
      for line in lines:
        if line != "":
          f.write(line+"\n")       

    f.write("\n</source_library>\n")

    f.close()

    if os.path.exists(output_srcs_list):
      print "File",output_srcs_list,"has been written"

  print  
      
  return

######################################################################

if __name__ == "__main__":

  parameters = ['InSrcModel','Request','OutSrcModel']
  
  if len(sys.argv) <= len(parameters):
    parameters_list = ""
    for ip in range(len(parameters)):
      parameters_list += parameters[ip] + " "
    print "\nSyntax : ",sys.argv[0],parameters_list
    print "  where: InSrcModel is a list of sources described in XML format."
    print "         OutSrcModel the name of output file in XML format."
    print "         Request is a logical python expression : "
    print "           Examples:  \"TS_value>100. and Integral > 0.1 \""
    print "                    \"dist((RA,DEC),(129.26,-45.45))<10.\""
    print "                    \"abs(glat(RA,DEC))<10.\""
    print "              where: dist : Distance in degrees  "
    print "                          between two directions on"
    print "                          the sky either (ra,dec) or (l,b)   "
    print "                     glat : Galactic latitude as a function "
    print "                          of Equatorial coordinates "
    print "                     glon : Galactic longitude as a function "
    print "                          of Equatorial coordinates "
    print ""
    print "Typing \"\" for request will display the list of variables,"
    print "available in the Input XML file. "
    print "XML object are defined by attributes,and elements which have their own"
    print "attributes. An attribute of  an element is written : attribute(element)"
    print "For example: scale(RA)"
    print "By default, the elements of the source take the contents of attribute value."
    print "For example, RA = value(RA), not scaled \n"
    sys.exit()
#
  InSrcModel = sys.argv[1]

  Request = sys.argv[2] 

  OutSrcModel = sys.argv[3] 
#
  search_Srcs(InSrcModel,
              Request,
              OutSrcModel)

  sys.exit()
