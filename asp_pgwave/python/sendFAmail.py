import smtplib
_servername="smtpunix.slac.stanford.edu"
def sendFAmail(sender,rec,subject,testo):
	headers="From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender,rec,subject)
	message=headers+testo
	#print message
	server=smtplib.SMTP(_servername)
	server.sendmail(sender, rec, message)
	server.quit()

if __name__=='__main__':

	_fromaddress="tosti@slac.stanford.edu"
	_toaddress=['tosti@pg.infn.it']
	subject='test FA mail'
	testo='questa e\' una prova'
	sendFAmail(_fromaddress,_toaddress,subject,testo)
