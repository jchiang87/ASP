import os,sys
from readpgw import *
def OpenModel():
 	print """<?xml version=\"1.0\" ?>
		<source_library title=\"source library\">"""
		

def AddSource(name,ra,dec,flux=2,sp=-2.2):
	print ("  <source name=\"%s\" type=\"PointSource\">" % name)
    	print "    <spectrum type=\"PowerLaw2\">"
      	print ("      <parameter error=\"0.00\" free=\"1\" max=\"1000\" min=\"1e-05\" name=\"Integral\" scale=\"1e-06\" value=\"%5.3f\"/>" % flux)
      	print ("      <parameter error=\"0.00\" free=\"1\" max=\"0\" min=\"-5\" name=\"Index\" scale=\"1\" value=\"%5.3f\"/>" % sp)
      	print "      <parameter free=\"0\" max=\"3e5\" min=\"20\" name=\"LowerLimit\" scale=\"1\" value=\"100\"/>"
      	print "      <parameter free=\"0\" max=\"3e5\" min=\"20\" name=\"UpperLimit\" scale=\"1\" value=\"200000\"/>"
    	print "    </spectrum>"
    	print "    <spatialModel type=\"SkyDirFunction\">"
      	print ("      <parameter free=\"0\" max=\"360\" min=\"-360\" name=\"RA\" scale=\"1\" value=\"%s\"/>" % ra)
      	print ("      <parameter free=\"0\" max=\"90\" min=\"-90\" name=\"DEC\" scale=\"1\" value=\"%s\"/>" % dec)
    	print "    </spatialModel>"
	print "  </source>"

def AddGalDiff():
	print """  <source name=\"Galactic Diffuse\" type=\"DiffuseSource\">
   <spectrum type=\"ConstantValue\">
      <parameter free=\"0\" max=\"10.0\" min=\"0.0\" name=\"Value\" scale=\"1\" value=\"1\"/>
   </spectrum>
   <spatialModel file=\"$(EXTFILESSYS)/galdiffuse/GP_gamma.fits\" type=\"MapCubeFunction\">
      <parameter free=\"0\" max=\"1000.0\" min=\"0.001\" name=\"Normalization\" scale=\"1.0\" value=\"1.0\"/>
   </spatialModel>  
  </source>"""
	
def AddExtraGal():
	print """  <source name=\"Extragalactic Diffuse\" type=\"DiffuseSource\">
   <spectrum type=\"PowerLaw\">
    <parameter error=\"0.289864\" free=\"1\" max=\"100.0\" min=\"1e-05\" name=\"Prefactor\" scale=\"1e-07\" value=\"1.65213\"/>
    <parameter free=\"0\" max=\"-1.0\" min=\"-3.5\" name=\"Index\" scale=\"1.0\" value=\"-2.1\"/>
    <parameter free=\"0\" max=\"200.0\" min=\"50.0\" name=\"Scale\" scale=\"1.0\" value=\"100.0\"/>
   </spectrum>
   <spatialModel type=\"ConstantValue\">
    <parameter free=\"0\" max=\"10.0\" min=\"0.0\" name=\"Value\" scale=\"1.0\" value=\"1.0\"/>
   </spatialModel>
  </source>"""

def CloseModel():
	print "</source_library>"

if __name__== "__main__":
              #name,flux,errflu,ind,errind=
	#name,typ,ra,dec=scanDRPModel('DRP_MergedList.xml')
	pgwfile=sys.argv[1]
	
	pg_name,pg_ra,pg_dec,signi=readpgw(pgwfile)
	OpenModel()
	for i in range(0,len(pg_ra)):
		AddSource(pg_name[i],pg_ra[i],pg_dec[i])
	AddGalDiff()
	AddExtraGal()
	CloseModel()
		
