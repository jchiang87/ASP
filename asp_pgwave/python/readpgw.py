def readpgw(filein):
	f=open(filein,'r')
	rows=f.readlines()
	
	nome=[]
	ra=[]
	dec=[]
	sn=[]
	signi=[]
	poserr=[]	
	source='PGW_'
	for i in range(1,len(rows)):
	    r=rows[i].split()
	    nome.append(("%s%04d"%(source,int(r[0]))))
	    ra.append(float(r[3]))
	    dec.append(float(r[4]))
	    poserr.append(float(r[5]))
	    signi.append(float(r[7]))
	f.close() 
	return nome,ra,dec,poserr,signi

if __name__ == "__main__":

	name_pgw,ra_pgw,dec_pgw,signi_pgw=readpgw('NorthPole_map.list')
	print name_pgw
