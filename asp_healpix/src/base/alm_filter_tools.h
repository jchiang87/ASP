/** @file alm_filter_tools.h
@brief implementation of several optimal filters, from astroph/0612688

@author M. Roth 

$Header$
*/

#include "xcomplex.h"
#include "arr.h"
#include "alm_map_tools.h"
#include <cmath>

template<typename T> class Alm;
template<typename T> class Healpix_Map;
class PowSpec;

/**@brief matched filter with constant background
@param sky  healpix fits file with signal and background
@param psf  healpix fits file with point spread function template
*/
template<typename T> void mf_constantnoise(Alm<T> &sky,Alm<T> &psf);

/**@brief matched filter with varied background
@param sky  healpix fits file with signal and background
@param psf  healpix fits file with point spread function template
@param noise  healpix fits file with background
*/
template<typename T> void mf_noise(Alm<T> &sky, Alm<T> &psf, Alm<T> &noise);

/**@brief scale adaptive filter with constant background
@param sky  healpix fits file with signal and background
@param psf  healpix fits file with point spread function template
@param cnl  magnitude of constant poisson noise power spectrum
*/
template<typename T> void saf_constantnoise(Alm<T> &sky,Alm<T> &psf,double cnl);

/**@brief scale adaptive filter with varied background
@param sky  healpix fits file with signal and background
@param psf  healpix fits file with point spread function template
@param noise  healpix fits file with background
*/
template<typename T> void saf_noise(Alm<T> &sky,Alm<T> &psf,Alm<T> &noise);


//------------------DILATED SPHERICAL FFTS-------------------------//
//                Added for filtering support                      //

/**@brief computes spherical harmonics at L2 norm preserving coordinates see arxiv:astro-ph/0612688
*/
template<typename T> void map2almdil(const Healpix_Map<T> &map,Alm<xcomplex<T> > &alm, 
									 const arr<double> &weight, double R, bool add_alm=false);

/**@brief iterative method of harmonic calculation with weights
*/
template<typename T> void map2alm_iterdil (const Healpix_Map<T> &map,
  Alm<xcomplex<T> > &alm, int num_iter, const arr<double> &weight, double R);

/**@brief iterative method of harmonic calculation without weights
*/
template<typename T> void map2alm_iterdil (const Healpix_Map<T> &map,
  Alm<xcomplex<T> > &alm, int num_iter, double R)
  {
  arr<double> wgt(2*map.Nside());
  wgt.fill(1);
  map2alm_iterdil(map,alm,num_iter,wgt,R);
  }
//
//------------------------------------------------------------------//

/**@brief likelood filter template in a healpix map centered at the north pole
@param level  order of healpix map
*/
  template<typename T> Healpix_Map<T> lhood(int level);
