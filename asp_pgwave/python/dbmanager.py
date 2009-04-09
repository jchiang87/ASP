import cx_Oracle
from datetime import datetime
from databaseAccess import apply,asp_default, glastgen
import astroUtil as ast
from math import *
_dbtables={'LightCurves':'LightCurves', \
 'FlareEvents':'FlareEvents',\
 'PointSources':'PointSources',\
 'EnergyBands':'EnergyBands',\
 'LatSourceCatalog':'LatSourceCatalog',\
 'DiffuseSources':'DiffuseSources',\
 'TimeIntervals':'TimeIntervals',\
 'Rois':'Rois',\
 'SourceMonitoringConfig':'SourceMonitoringConfig',\
 'Frequencies':'Frequencies',\
 'FlareTestTypes':'FlareTestTypes',\
 'FlareTypes':'FlareTypes',\
 'Flare_COUNTERPART':'Flare_COUNTERPART',\
 'SpectrumTypes':'SpectrumTypes',\
 'SourceTypes':'SourceTypes',\
 'GCNnotices':'GCNnotices',\
 'GRB_Email_List':'GRB_Email_List',\
 'GRB_ASP_Config':'GRB_ASP_Config',\
 'GRBAfterglow':'GRBAfterglow',\
 'GRB':'GRB',\
 'Healpix':'Healpix',\
 'FlareAdvocateResults':'FlareAdvocateResults',\
 'CounterPartCatalog':'CounterPartCatalog'}
 
_FlareTypesFields={'flare_type':('flare_type',[])}

_FlareTestTypesFields={'flare_test_type':('flare_test_type',[])}

_PointSourcesFields={
  'PTSRC_NAME':('ptsrc_name',[]),\
  'HEALPIX_ID':('healpix_id',[]),\
  'ROI_ID':('roi_id',[]),\
  'LAT_CATID':('lat_catid',[]),\
  'SOURCE_TYPE':('source_type',[]),\
  'SPECTRUM_TYPE':('spectrum_type',[]),\
  'RA':('ra',[]),\
  'DEC':('dec',[]),\
  'ERROR_RADIUS':('error_radius',[]),\
  'POSITION_QUALITY':('position_quality',[]),\
  'NX':('nx',[]),\
  'NY':('ny',[]),\
  'NZ':('nz',[]),\
  'XML_MODEL':('xml_model',[]),\
  'IS_OBSOLETE':('is_obsolete',[]),\
  'IS_PUBLIC':('is_public',[]),
  'ALIAS' : ('alias', [])}
  
_CounterPartFields={
  'CATALOGNAME':('catalogname',[]),\
  'COUNTERPARTNAME':('counterpartname',[]),\
  'RA':('ra',[]),\
  'DEC':('dec',[]),\
  'ERROR_RADIUS':('error_radius',[])}

_FlareCounterpatFields={
  'FLARE_ID':('flare_id',[]),\
  'CATALOGNAME':('catalogname',[]),\
  'COUNTERPARTNAME':('counterpartname',[])}

_FlareEventsFields={
  'FLARE_ID':('flare_id',[]),\
  'PTSRC_NAME':('ptsrc_name',[]),\
  'ADVOCATE_RESULT_ID':('advocate_result_id',[]),\
  'STARTTIME':('starttime',[]),\
  'ENDTIME':('endtime',[]),\
  'FLUX':('flux',[]),\
  'FLUX_ERR':('flux_err',[]),\
  'FLARE_TYPE':('flare_type',[]),\
  'FLARE_TEST_TYPE':('flare_test_type',[]),\
  'FLARE_TEST_VALUE':('flare_test_value',[]),\
  'PROCESSING_DATE':('processing_date',[]),\
  'HEALPIX_ID':('healpix_id',[])}

class dbmanager:
	def __init__(self,connect=asp_default):
		self.conn= cx_Oracle.connect(*connect)
	def close(self):
		self.conn.close()
	def getPointSources(self):
                sql = "select a.* from PointSources a left join PointSourceTypeSet b  on (a.ptsrc_name = b.ptsrc_name)  where ((b.sourcesub_type = 'DRP' or b.sourcesub_type = 'BLZRGRPSRC' or b.sourcesub_type='KNOWNPSR' or b.sourcesub_type='PGWAVE')) order by ra ASC"
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		colname=cursor.description
		tot=len(colname)
		for row in cursor:
		  for i in range(0,tot):
		    _PointSourcesFields[colname[i][0]][1].append(row[i])
		cursor.close()
	def getPgwaveConfig(self):
		sql="select * from pgwaveconfig  order by version_id desc"
		print sql
		cursor=self.conn.cursor()                
		res=cursor.execute(sql)
		nrec=cursor.fetchone()
		#print cursor.description
		#for it in cursor:
		#    print it
		cursor.close()
		return nrec
	def setPgwaveConfigDef(self):
		sql="insert into pgwaveconfig(version_id,tstamp,pgw_nwav_scale,pgw_wav_scale,pgw_k_sigma_thres,pgw_noverthresh_pix,pgw_ntime_bin,pgw_chi2_thresh) values(1,current_timestamp,1,'3.0','10',3,5,10)"
		print sql
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		self.conn.commit()
		cursor.close()
        def getPointSourcesFSP(self):     
	        sql="select count(*) from POINTSOURCES where source_type='Other_FSP'"
               	cursor=self.conn.cursor()                
		res=cursor.execute(sql)                
		nrec=cursor.fetchone()
		no=[]
		if nrec[0]>0:
			sql="select ptsrc_name from POINTSOURCES where source_type='DRP'"
			res=cursor.execute(sql)
			for it in cursor:
				no.append(it[0])	          
		cursor.close()
		return no
	def getNrec(self,table):
		sql=("select count(*) from %s" % table)
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		nrec=cursor.fetchone()
		cursor.close()
		return nrec[0]
   	def deleteDuplicateFE(self,procid):
		sql = ("delete from flareevents where process_id=%i" % procid)
		cursor=self.conn.cursor()
		res=cursor.execute(sql)
		self.conn.commit()
		cursor.close()
	def insertFlareEvent(self,nome,tstart,tstop,flux,err,chi,ff,confid,procid):
                if err != err:
                        # Have nan from pgwave so return without trying to insert
                        return
		cursor=self.conn.cursor()
		sql="select flareevents_Seq.nextval from dual"
		res=cursor.execute(sql)
		nrec=cursor.fetchone()
		#print nrec[0]
		sql2="insert into flareevents(flare_id,ptsrc_name,starttime,endtime,flux,flux_err,flare_test_type,flare_test_value,processing_date,flaring_flag,pgwaveconfig_id,process_id) "
		sql3= ("values(%i,'%s',%i,%i,%.2e,%.2e,'Chi2',%.2f,current_timestamp,%i,%i,%i)" % (nrec[0],nome,tstart,tstop,flux,err,chi,ff,confid,procid))
		sql4=sql2+sql3
		print sql4
		res=cursor.execute(sql4)
		self.conn.commit()
		"""sql="select * from flareevents"
		res=cursor.execute(sql)
		for it in cursor:
			print it"""			    
		cursor.close()
	def insertPointSource(self,heaid,ra,dec,err):
		r = ra*3.14159265358979/180.
       		d = dec*3.14159265358979/180.
       		dir = ( cos(r)*cos(d), sin(r)*cos(d) , sin(d) ) 
        	cursor=self.conn.cursor()
		sql="select pgwave_Seq.nextval from dual"                
		res=cursor.execute(sql)
                nrec=cursor.fetchone()
		nome=('FSP_%05d' % nrec[0])
		nome1='ASPJ'+ast.sphd2shptext(ra,dec)
                #
                # Check if this source is already in the table.
                #
                my_sql = ("select PTSRC_NAME from POINTSOURCES " +
                          "where PTSRC_NAME='%s'" % nome1)
                cursor.execute(my_sql)
                ptsrc_name = cursor.fetchone()
                if ptsrc_name is None:
                        sql2="insert into pointsources(ptsrc_name,healpix_id,source_type,ra,dec,error_radius,nx,ny,nz,is_obsolete,is_public) "
                        sql3= ("values('%s',%i,'Other_FSP',%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,0,0)" % (nome1,heaid,ra,dec,err,dir[0],dir[1],dir[2]))
                        sql4=sql2+sql3
        	        #print sql4
                        res=cursor.execute(sql4)
                        self.conn.commit()
                        #
                        # insert subtype into pointsourcetypeset table
                        #
                        sql = "insert into pointsourcetypeset (ptsrc_name, sourcesub_type) values ('%s', 'PGWAVE')" % nome1
                        print sql
                        cursor.execute(sql)
                        self.conn.commit()
		cursor.close()	
		return nome1

def FAdvocateEmails():
    	    sql = """select u.first_name,u.last_name,u.email from profile_user u join profile_ug ug on ug.user_id=u.user_name 
         where group_id in
         (select group_name from profile_group 
          left outer join profile_gg on parent_id = group_name 
          start with group_name='FlareAdvocate' 
          connect by prior group_name = child_id)
         group by u.first_name,u.last_name,u.email"""
	 
            try:
        	email_list = apply(sql, lambda curs : [x[2] for x in curs], 
                           connection=glastgen)
    	    except:
		#print "test"
        	email_list = ['tosti@pg.infn.it']
    	    return email_list

def getSMIrf(tstart):
    sql = "select * from SOURCEMONITORINGCONFIG"
    def findConfig(cursor):
        for entry in cursor:
            startdate, enddate = entry[1], entry[2]
	    #print entry[1], entry[2],entry[3]
            if startdate <= tstart and tstart <= enddate:
                return entry[3]
        message = 'SourceMonitoring configuration not found for %i MET' % tstart
        raise RuntimeError, message
    irfs =apply(sql, findConfig)
    return irfs




if __name__=="__main__":

	#d=datetime.now()
	#db=dbmanager()
	#db.getPointSources()
	#n=db.insertFlareEvent('3C 279',2555000,2500000,3e-7,3e-8,2.6,0)
	#no=db.getPointSourcesFSP()
	#if len(no)>0:
	#	print no
	#db.setPgwaveConfigDef()
	#no=db.getPgwaveConfig()
	#print no[3]
	#db.close()
	email=FAdvocateEmails()
	print email
	#getSMIrf()
	#print _PointSourcesFields['HEALPIX_ID'][1]
