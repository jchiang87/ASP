#
# $Header$
#
import os,sys
import matplotlib
matplotlib.use('Agg')

os.environ['HOME'] = os.environ['OUTPUTDIR']

import pylab as pl
import numpy.numarray.fft as nff
import numpy as num
import pyfits

def ConvFilter(image1, image2, pad=True, MinPad=True, Smooth=False):

	r1,c1  = image1.shape
	r2,c2  = image2.shape

	#Padding to the end. Inserting to the middle would
	#break up the resulted image.
	#The window filled within:

	if MinPad:
		x1 = r1 + r2 -1
		y1 = c1 + c2 -1
	else :
		x1 = 2 * max(r1,r2)
		y1 = 2 * max(c1,c2)

	Fft = nff.fft2d
	iFft = nff.inverse_fft2d

	if pad:
		#round up to the next power of two:
		px2 = int(num.log(x1)/num.log(2.0) + 1.0)
		py2 = int(num.log(y1)/num.log(2.0) + 1.0)
		xOrig = x1
		yOrig = y1
		x1 = 2**px2
		y1 = 2**py2

	if Smooth:
		fftimage = Fft(image1, s=(x1,y1)) * Fft(image2,s=(x1,y1))
	else :
		fftimage = Fft(image1, s=(x1,y1)) * \
				Fft(image2[::-1,::-1],s=(x1,y1))
		Fft(image2, s=(x1,y1)).conjugate()*indx

	if pad:

		return ((iFft(fftimage))[:xOrig,:yOrig]).real

	else :
		#return abs(iFft(fftimage))
		return (iFft(fftimage)).real

def GaussKernel(r=10, width=0, norm=False):

	size = 2*r+1

	if width == 0:
		width = r

	const = -4.0*num.log(2.0)/(width**2)
	kernelcore = num.indices((size,size))
	
	kernel = num.exp(const*((kernelcore[0]-r)**2 +(kernelcore[1]-r)**2))

	if norm:
		#Normalize to 1:
		kernel = kernel/kernel.sum()
	
	return kernel
 
def plotCircle(x,y, size=0):
        t = pl.arange(-3.14,3.14,0.03)
        pl.axis('image')
        pl.plot(x,y,'r+')
        k=1
        for x1,y1 in zip (x,y):


                if size == 0:
                        r = 6. #num.sqrt(float(res['size'][i]))/2
                else :
                        r = size


                if y1<200 and y1>160:
                        pl.plot((x1+r*num.cos(t)),(y1+r*num.sin(t)),'r-')
                        #pl.text(x1, y1+size+size*0.2,("%d"%k),bbox=dict(facecolor='w',alpha=0.5),color='k')
                else:
                        pl.plot((x1+r*num.cos(t)),(y1+r*num.sin(t)),'w-')
                        #pl.text(x1, y1+size+size*0.15,str(k),color='w')
                k+=1

        #pl.draw()
        return

def aitoff1(l,b):
        conv=num.pi/180.000000000
        l1=l*conv
        b1=b*conv

        for i in range(0,l1.size):
                if l1[i]< num.pi:
                        l1[i]=-l1[i]
                else:
                        l1[i]=2.*num.pi-l1[i]
        rp=l1/2.
        du=num.sqrt(1.+num.cos(b1)*num.cos(rp))
        x=(2.*num.cos(b1)*num.sin(rp))/du
        y= num.sin(b1)/du
        x=32+(2.+x)*650/4.
        y=16.+(1.+y)*325/2.
        #for x0,y0,l0,b0 in zip(x,y,l,b):
                #print l0,b0,x0,y0
        return x,y


def creaXimageGif(nomefile,l,b):

 	#f=open("temp.xco","w")
	#outgif=nomefile.replace('.fits','_.gif')
 	#f.write("read_image %s\nchat 0\ncpd %s/gif\ncct/set vt1\nsmo/real/sigma=1.2\ndisp/lin/nof\nexit\n" % (nomefile,outgif))
	#f.close()
	im,hdr=pyfits.getdata(nomefile,header='True')
	im.shape=(hdr['NAXIS2'],hdr['NAXIS1']) 
	kernel=GaussKernel(10,2.5,norm=True)
	out=ConvFilter(im, kernel,Smooth=True)
	out=out[12:372,12:732]
	w,h=im.shape
	pl.figure(figsize=(h/72, w/72),dpi=72)
	pl.axes((0,0,1,1))
	pl.axis('off')
	pl.imshow(pl.log(out+1),cmap=pl.cm.jet,origin='lower',interpolation='bilinear')
	outgif1=nomefile.replace('.fits','.png')
	x,y=aitoff1(l,b)
	plotCircle(x,y,6)
	pl.savefig(outgif1,dpi=72)
	pl.clf()
	pl.close('all')
	outgif=nomefile.replace('.fits','.gif')
	#comando="ximage @temp.xco" 
	#comando1= ("convert %s -crop 575x285+180+165 %s\n" % (outgif,outgif1))
	comando1= ("convert %s %s\n" % (outgif1,outgif))
	#print comando1
	try:
		#os.system(comando)
		os.system(comando1)
		
	except:
		print "@error while trying to create gif"

        #
        # Ensure a file exists, to enable data registration process later
        #
        os.system('touch %s' % outgif)
	
	#os.remove(outgif)	
	
if __name__ == '__main__':
	creaXimageGif(sys.argv[1],l,b)


