#include "healpix/base/alm_filter_tools.h"
#include "healpix/base/alm.h"
#include "healpix/base/powspec.h"
#include "healpix/base/alm_powspec_tools.h"
#include "healpix/base/healpix_map.h"
#include "healpix/base/fftpack_support.h"
#include "healpix/base/ylmgen.h"
#include "healpix/base/openmp_support.h"
using namespace std;

template<typename T> void mf_constantnoise(Alm<T> &sky,Alm<T> &psf) {
	PowSpec pmap(1,sky.Lmax());
	extract_powspec(psf,pmap);
	double a = 0;
	for(int l=0;l<=pmap.Lmax();l++) {
		a += pmap.tt()[l]*(2*l+1);
	}
	psf.Scale(1/a);
	psf = conjugate(psf);
	arr<T> scale(pmap.Lmax()+1,0);
	for(int l=0;l<=pmap.Lmax();l++) {
		T fact = sqrt(4*pi/(2*l+1));
		scale[l] = fact*psf(l,0);
	}
	sky.ScaleL(scale);
}

template void mf_constantnoise(Alm<xcomplex<float> > &sky,Alm<xcomplex<float> > &psf);
template void mf_constantnoise(Alm<xcomplex<double> > &sky,Alm<xcomplex<double> > &psf);

template<typename T> void mf_noise(Alm<T> &sky,Alm<T> &psf, Alm<T> &noise) {
	PowSpec pmap(1,sky.Lmax());
	extract_powspec(psf,pmap);
	PowSpec pnoise(1,sky.Lmax());
	extract_powspec(noise,pnoise);
	double a = 0;
	for(int l=0;l<=pmap.Lmax();l++) {
		a += pmap.tt()[l]/pnoise.tt()[l]*(2*l+1);
	}
	psf.Scale(1/a);
	psf = conjugate(psf);
	arr<T> scale(pmap.Lmax()+1,0);
	for(int l=0;l<=pmap.Lmax();l++) {
		T fact = sqrt(4*pi/(2*l+1));
		T fact2 = 1/pnoise.tt()[l];
		scale[l] = fact*psf(l,0)*fact2;
	}
	sky.ScaleL(scale);
}

template void mf_noise(Alm<xcomplex<float> > &sky,Alm<xcomplex<float> > &psf, Alm<xcomplex<float> > &noise);
template void mf_noise(Alm<xcomplex<double> > &sky,Alm<xcomplex<double> > &psf, Alm<xcomplex<double> > &noise);

template<typename T> void saf_constantnoise(Alm<T> &sky,Alm<T> &psf,double cnl){
	PowSpec pmap(1,psf.Lmax());
	extract_powspec(psf,pmap);
	double a = 0;
	xcomplex<double> b(0,0);
	xcomplex<double> c(0,0);
	for(int l=1;l<=psf.Lmax();l++) {
		a += (2*l+1)*pmap.tt()[l]/cnl;
		xcomplex<double> fact(l/cnl,0);
		b += fact*(psf(l,0).conj()-psf(l-1,0));
		c += fact*(psf(l,0)-psf(l-1,0));
	}
	double del = sqrt((a*c-b.norm()).norm());
	arr<T> scale(psf.Lmax()+1,0);
	for(int l=1;l<=psf.Lmax();l++) {
		scale[l] = (c-b*l*(psf(l,0)-psf(l-1,0)));
	}
	sky.Scale(-1/(del*cnl));
	sky.ScaleL(scale);
}

template void saf_constantnoise(Alm<xcomplex<float> > &sky,Alm<xcomplex<float> > &psf, double cnl);
template void saf_constantnoise(Alm<xcomplex<double> > &sky,Alm<xcomplex<double> > &psf, double cnl);

template<typename T> void saf_noise(Alm<T> &sky,Alm<T> &psf,Alm<T> &noise){
	PowSpec pmap(1,psf.Lmax());
	extract_powspec(psf,pmap);
	PowSpec pnoise(1,noise.Lmax());
	extract_powspec(noise,pnoise);
	double a = 0;
	xcomplex<double> b(0,0);
	xcomplex<double> c(0,0);
	for(int l=1;l<=psf.Lmax();l++) {
		a += (2*l+1)*pmap.tt()[l]/pnoise.tt()[l];
		xcomplex<double> fact(l/pnoise.tt()[l],0);
		b += fact*(psf(l,0).conj()-psf(l-1,0));
		c += fact*(psf(l,0)-psf(l-1,0));
	}
	double del = sqrt((a*c-b.norm()).norm());
	arr<T> scale(psf.Lmax()+1,0);
	for(int l=1;l<=psf.Lmax();l++) {
		xcomplex<double> fact(1/pnoise.tt()[l],0);
		scale[l] = (c-b*l*(psf(l,0)-psf(l-1,0)))*fact;
	}
	sky.Scale(-1/del);
	sky.ScaleL(scale);
}

template void saf_noise(Alm<xcomplex<float> > &sky,Alm<xcomplex<float> > &psf, Alm<xcomplex<float> > &noise);
template void saf_noise(Alm<xcomplex<double> > &sky,Alm<xcomplex<double> > &psf, Alm<xcomplex<double> > &noise);


template<typename T> Alm<xcomplex<T> > conjugate(Alm<xcomplex<T> > &alm) {
	for(int l=0;l<=alm.Lmax();l++) {
		for(int m=0;m<=alm.Mmax();m++) {
			xcomplex<T> *it = alm.mstart(m);
			it[l].im = -alm.mstart(m)[l].im;
		}
	}
	return alm;
}

template Alm<xcomplex<float> > conjugate(Alm<xcomplex<float> > &alm);
template Alm<xcomplex<double> > conjugate(Alm<xcomplex<double> > &alm);

template<typename T> void map2almdil (const Healpix_Map<T> &map,
  Alm<xcomplex<T> > &alm, const arr<double> &weight, double R, bool add_alm)
  {
  planck_assert (map.Scheme()==RING, "map2alm: map must be in RING scheme");
  planck_assert (weight.size()>=2*map.Nside(),
    "map2alm: weight array has too few entries");

  int lmax = alm.Lmax(), mmax = alm.Mmax(), nside = map.Nside();

  int nchunks, chunksize;
  get_chunk_info(2*nside,nchunks,chunksize);

  arr2<xcomplex<double> > phas_n(chunksize,mmax+1), phas_s(chunksize,mmax+1);
  arr<double> cth(chunksize), sth(chunksize);
  double normfact = pi/(3*nside*nside);

  if (!add_alm) alm.SetToZero();

  for (int chunk=0; chunk<nchunks; ++chunk)
    {
    int llim=chunk*chunksize, ulim=min(llim+chunksize,2*nside);
#ifdef _OPENMP
#pragma omp parallel
#endif
{
    arr<xcomplex<double> > shiftarr(mmax+1), work(4*nside);
    rfft plan;

    int ith;
#ifdef _OPENMP
#pragma omp for schedule(dynamic,1)
#endif
    for (ith=llim; ith<ulim; ++ith)
      {
      int istart_north, istart_south, nph;
      bool shifted;
      map.get_ring_info (ith+1,istart_north,nph,cth[ith-llim],sth[ith-llim],
                         shifted);
      istart_south = 12*nside*nside - istart_north - nph;

      recalc_map2alm (nph, mmax, plan, shiftarr);
      fft_map2alm (nph, mmax, shifted, weight[ith]*normfact, plan,
        &map[istart_north], &map[istart_south], phas_n[ith-llim],
        phas_s[ith-llim], shiftarr, work);
      }
} // end of parallel region
#ifdef _OPENMP
#pragma omp parallel
#endif
{
    Ylmgen generator(lmax,mmax,1e-30);
    arr<double> Ylm;
    arr<xcomplex<double> > alm_tmp(lmax+1);
    int m;
#ifdef _OPENMP
#pragma omp for schedule(dynamic,1)
#endif
    for (m=0; m<=mmax; ++m)
      {
      for (int l=m; l<=lmax; ++l) alm_tmp[l].Set(0.,0.);
      for (int ith=0; ith<ulim-llim; ++ith)
        {
        int l;
		double tth2 = sth[ith]/(1+cth[ith]);
		double sthr = 2*R*tth2/(R*R*tth2*tth2+1);
		double cthr = (1-R*R*tth2*tth2)/(1+R*R*tth2*tth2);
		double lambda = 2*R/((R*R-1)*cthr+(R*R+1));
        generator.get_Ylm(cthr,sthr,m,Ylm,l);
        if (l<=lmax)
          {
          xcomplex<double> p1 = phas_n[ith][m]+phas_s[ith][m],
                           p2 = phas_n[ith][m]-phas_s[ith][m];

          if ((l-m)&1) goto middle;
start:    alm_tmp[l].re += p1.re*Ylm[l]/lambda; alm_tmp[l].im += p1.im*Ylm[l]/lambda;
          if (++l>lmax) goto end;
middle:   alm_tmp[l].re += p2.re*Ylm[l]/lambda; alm_tmp[l].im += p2.im*Ylm[l]/lambda;
          if (++l<=lmax) goto start;
end:      ;
          }
        }
      xcomplex<T> *palm = alm.mstart(m);
      for (int l=m; l<=lmax; ++l)
        { palm[l].re += alm_tmp[l].re; palm[l].im += alm_tmp[l].im; }
      }
} // end of parallel region
    }
  }
template void map2almdil (const Healpix_Map<float> &map,
  Alm<xcomplex<float> > &alm, const arr<double> &weight,
  double R, bool add_alm);
template void map2almdil (const Healpix_Map<double> &map,
  Alm<xcomplex<double> > &alm, const arr<double> &weight,
  double R, bool add_alm);

template<typename T> void map2alm_iterdil (const Healpix_Map<T> &map,
  Alm<xcomplex<T> > &alm, int num_iter, const arr<double> &weight, double R)
  {
  map2almdil(map,alm,weight,R);
  for (int iter=1; iter<=num_iter; ++iter)
    {
    Healpix_Map<T> map2(map.Nside(),map.Scheme(),SET_NSIDE);
    alm2map(alm,map2);
    for (int m=0; m<map.Npix(); ++m)
      map2[m] = map[m]-map2[m];
    map2alm(map2,alm,weight,true);
    }
  }

template void map2alm_iterdil (const Healpix_Map<float> &map,
  Alm<xcomplex<float> > &alm, int num_iter,
  const arr<double> &weight, double R);
template void map2alm_iterdil (const Healpix_Map<double> &map,
  Alm<xcomplex<double> > &alm, int num_iter,
  const arr<double> &weight, double R);

template<typename T> Healpix_Map<T> lhood(int level) {
	Healpix_Map<T> hm(level,::RING);
	arr<T> map(hm.Npix());
	double gamma = 2.5;
	int startpix, ringpix;
		double costheta, sintheta;
		bool shifted;
	for(int i = 1;i<=2*hm.Nside();i++) {
		hm.get_ring_info(i,startpix,ringpix,
			costheta, sintheta, shifted);
		double t = (1.-costheta)/(1.+costheta);
		double pipsi = (1-2*t)*pow(1+2*t/gamma,-gamma-2);
		for(int j=0; j<ringpix; j++) {
			map[j+startpix]=pipsi;
		}
	}
	hm.Set(map,::RING);
	return hm;
}

template Healpix_Map<float> lhood(int level);
template Healpix_Map<double> lhood(int level);


//------------------FFT misc functions-------------------//
//       unable to be resolved in global scope           //
namespace {

void init_lam_fact_1d (int m, arr<double> &lam_fact)
  {
  for (int l=m; l<lam_fact.size(); ++l)
    lam_fact[l] = (l<2) ? 0. : 2*sqrt((2*l+1.)/(2*l-1.) * (l*l-m*m));
  }

void init_lam_fact_deriv_1d (int m, arr<double> &lam_fact)
  {
  lam_fact[m]=0;
  for (int l=m+1; l<lam_fact.size(); ++l)
    lam_fact[l] = sqrt((2*l+1.)/(2*l-1.) * (l*l-m*m));
  }

void init_normal_l (arr<double> &normal_l)
  {
  for (int l=0; l<normal_l.size(); ++l)
    normal_l[l] = (l<2) ? 0. : sqrt(1./((l+2.)*(l+1.)*l*(l-1.)));
  }

void get_chunk_info (int nrings, int &nchunks, int &chunksize)
  {
  nchunks = nrings/max(100,nrings/10) + 1;
  chunksize = (nrings+nchunks-1)/nchunks;
  }

void fill_work (const xcomplex<double> *datain, int nph, int mmax,
  bool shifted, const arr<xcomplex<double> > &shiftarr,
  arr<xcomplex<double> > &work)
  {
  for (int m=1; m<nph; ++m) work[m]=0;
  work[0]=datain[0];

  int cnt1=0, cnt2=nph;
  for (int m=1; m<=mmax; ++m)
    {
    if (++cnt1==nph) cnt1=0;
    if (--cnt2==-1) cnt2=nph-1;
    xcomplex<double> tmp = shifted ? (datain[m]*shiftarr[m]) : datain[m];
    work[cnt1] += tmp;
    work[cnt2] += conj(tmp);
    }
  }

void read_work (const arr<xcomplex<double> >& work, int nph, int mmax,
  bool shifted, const arr<xcomplex<double> > &shiftarr,
  xcomplex<double> *dataout)
  {
  int cnt2=0;
  for (int m=0; m<=mmax; ++m)
    {
    dataout[m] = work[cnt2];
    if (++cnt2==nph) cnt2=0;
    }
  if (shifted)
    for (int m=0; m<=mmax; ++m) dataout[m] *= shiftarr[m];
  }

void recalc_map2alm (int nph, int mmax, rfft &plan,
  arr<xcomplex<double> > &shiftarr)
  {
  if (plan.size() == nph) return;
  plan.Set (nph);
  double f1 = pi/nph;
  for (int m=0; m<=mmax; ++m)
    {
    if (m<nph)
      shiftarr[m].Set (cos(m*f1),-sin(m*f1));
    else
      shiftarr[m]=-shiftarr[m-nph];
    }
  }

template<typename T> void fft_map2alm (int nph, int mmax, bool shifted,
  double weight, rfft &plan, T *mapN, T *mapS,
  xcomplex<double> *phas_n, xcomplex<double> *phas_s,
  const arr<xcomplex<double> > &shiftarr, arr<xcomplex<double> > &work)
  {
  for (int m=0; m<nph; ++m) work[m] = mapN[m]*weight;
  plan.forward_c(work);
  read_work (work, nph, mmax, shifted, shiftarr, phas_n);
  if (mapN!=mapS)
    {
    for (int m=0; m<nph; ++m) work[m] = mapS[m]*weight;
    plan.forward_c(work);
    read_work (work, nph, mmax, shifted, shiftarr, phas_s);
    }
  else
    for (int m=0; m<=mmax; ++m) phas_s[m]=0;
  }

void recalc_alm2map (int nph, int mmax, rfft &plan,
  arr<xcomplex<double> > &shiftarr)
  {
  if (plan.size() == nph) return;
  plan.Set (nph);
  double f1 = pi/nph;
  for (int m=0; m<=mmax; ++m)
    {
    if (m<nph)
      shiftarr[m].Set (cos(m*f1),sin(m*f1));
    else
      shiftarr[m]=-shiftarr[m-nph];
    }
  }

template<typename T> void fft_alm2map (int nph, int mmax, bool shifted,
  rfft &plan, T *mapN, T *mapS, xcomplex<double> *b_north,
  xcomplex<double> *b_south, const arr<xcomplex<double> > &shiftarr,
  arr<xcomplex<double> > &work)
  {
  fill_work (b_north, nph, mmax, shifted, shiftarr, work);
  plan.backward_c(work);
  for (int m=0; m<nph; ++m) mapN[m] = work[m].re;
  if (mapN==mapS) return;
  fill_work (b_south, nph, mmax, shifted, shiftarr, work);
  plan.backward_c(work);
  for (int m=0; m<nph; ++m) mapS[m] = work[m].re;
  }

} // namespace
//
//-------------------------------------------------------------------------//
