/**
 * @file HealpixArray.h
 * @brief Subclass of healpix::HealpixArray<float> with added FITS I/O
 * member functions.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef _AspHealPix_HealpixArray_h
#define _AspHealPix_HealpixArray_h

#include <stdexcept>

#include "astro/SkyDir.h"
#include "astro/SkyFunction.h"

#include "healpix/Healpix.h"
#include "healpix/HealpixArray.h"

#include "Pixel.h"
/**
 * @class HealpixArray
 *
 */

class HealpixArray : public healpix::HealpixArray<float>,
                     public astro::SkyFunction {
public:

   HealpixArray();

   HealpixArray(healpix::Healpix hp);

   HealpixArray(const std::string & infile, 
                const std::string & extname,
                const std::string & fieldname);

   virtual ~HealpixArray();

   virtual void write(const std::string & outfile, 
                      const std::string & extname,
                      const std::string & fieldname) const;

   virtual void writeImage(const std::string & outfile,
                           double pixel_size = 0.5,
                           bool galactic = true) const;

   virtual HealpixArray operator+(const HealpixArray & x) const;
   virtual HealpixArray operator-(const HealpixArray & x) const;
   virtual HealpixArray operator*(const HealpixArray & x) const;
   virtual HealpixArray operator/(const HealpixArray & x) const;

   virtual HealpixArray operator+(double x) const;
   virtual HealpixArray operator-(double x) const;
   virtual HealpixArray operator*(double x) const;
   virtual HealpixArray operator/(double x) const;

   virtual HealpixArray operator-() const;

   virtual double operator()(const astro::SkyDir & dir) const;

   healpix::Healpix healpix() const;

   const std::vector<float> & values() const;

   const std::vector<float> & glon() const;
   const std::vector<float> & glat() const;

   static void writeLayeredImage(const std::vector<HealpixArray> & arrays,
                                 const std::string & outfile, 
                                 double pixel_size=0.5, bool galactic=true);

   HealpixArray HealpixArray::inverse();
   void HealpixArray::subSelect(
                                const std::string& infile, 
                                const std::string& outfile, 
                                long idx, 
                                const std::string & extname="EVENTS");

private:

   std::vector<float> m_glon;
   std::vector<float> m_glat;

   void fillCoordArrays();

   astro::SkyDir::CoordSystem coordsys(const std::string & infile,
                                       const std::string & extname) const;


};

inline HealpixArray operator+(double left, const HealpixArray & right) {
   return right + left;
}

inline HealpixArray operator-(double left, const HealpixArray & right) {
   return -(right - left);
}

inline HealpixArray operator*(double left, const HealpixArray & right) {
   return right*left;
}

#endif // _AspHealPix_HealpixArray_h
