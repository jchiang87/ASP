/** @file Map.h
@brief Wrapper for the JPL healpix class of a sky map, including Optimal Filters for the sphere

@author M. Roth 

$Header$
*/
#include <string>
#include <vector>
#include "src/base/healpix_map.h"
#include "src/base/powspec.h"
#include "astro/SkyFunction.h"
#include "healpix/HealPixel.h"

namespace healpix {


    template<typename T> class Map : public astro::SkyFunction {
        /**
        @class Map<T>
        @brief Encapsulates the healpix C++ class Healpix_Map, a map data array
        see "healpix_map.h" for more information on methods

        The fits file needs to be in a healpix_map format (fits format can be generated from ROOT files with Convolution package)

        Usage:
        @verbatim

        Map<double> map("map.fits",level);
        map.mfcn(lmax);  //applies a matched filter to the data

        @endverbatim

        */	
    public:
        /**@brief constructor takes healpix fits filename and bin level (level = 12*2**nside)
        @param file  FITS file location   "X:\\folder\\folder\\file.fits"
        @param level  binning level defined by energy binner from map_tools package
        */
        Map<T>(const std::string &file, int level);

        /**@brief constructor with empty map and a bin level
        @param level  binning level defined by energy binner from photon_data package
        */
        Map<T>(int level);

        Map<T>(const astro::SkyFunction& sf, int level);

        /**@brief returns a reference to the Healpix map
        */
        Healpix_Map< T>* map();

        /**@brief returns a constant reference to the Healpix map (time-intensive)
        */
        const Healpix_Map< T>* cmap() const { return &m_hm;}

        /**@brief returns an array where a[i] is the ith moment of the angular power spectrum up to lmax
        */
        std::vector<T> powspec(int lmax);

        /**@brief scales every element in the map by factor
        */
        void scale(T factor);

        /**@brief if element is less than zero, sets to zero
        */
        void zeromap();

        /**@brief addition operator: map will have nside = max(this.nside,other.nside), ie the higher resolution
        */
        Map<T> operator+(Map<T> &other);

        /**@brief applies a matched filter . The filter kernel is derived from a 
        fits file "LHOOD.fits"
        @param psffile  FITS file location   "X:\\folder\\folder\\file.fits"
        @param lmax  maximum multipole moment
        */
        void mfcn(const std::string &psffile,int lmax);

        /**@brief applies a matched filter with simple point spread function of energy E
        @param lmax  maximum multipole moment
        @param energy  determines width of point spread function
        */
        void mfcn(int lmax, double energy);

        /**@brief applies a matched filter with a varied background
        @param noise  file of noise
        @param lmax  maximum multipole moment
        */
        void mfvn(Map<T> &nhm, int lmax, double energy);

        /**@brief writes a FITS file out in the HEALpix convention
        @param out  FITS file location   "X:\\folder\\folder\\file.fits"
        */
        void writemap(std::string &out);

        /**@brife returns map value in a particular direction by closest HealPixel
        @param sd  direction to look 
        */
        double operator()(const astro::SkyDir & sd) const{ return m_hm[m_hm.nest2ring(healpix::HealPixel(sd,m_hm.Order()).index())];}


    private:
        double m_factor;      //binning factors: E = s_minenergy*m_factor**(level-s_minlevel)
	Healpix_Map< T> m_hm; //wrapped HEALpix package map object
        static const int s_minlevel = 6;
        static const int s_minenergy = 100;
    };

} //namespace
