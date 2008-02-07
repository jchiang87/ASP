/**
 * @file Pixel.h
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef _AspHealPix_Pixel_h
#define _AspHealPix_Pixel_h

#include "astro/SkyDir.h"

#include "healpix/Healpix.h"

class Pixel : public healpix::Healpix::Pixel {

public:
   /// @brief construct a pixel from the index
   Pixel(long index, const healpix::Healpix & hp) 
      : healpix::Healpix::Pixel(index, hp) {}

   /// @brief create a Pixel from a direction
   Pixel(const astro::SkyDir& dir, const healpix::Healpix& hp) 
      : healpix::Healpix::Pixel(dir, hp) {}

   Pixel(const healpix::Healpix::Pixel & my_pix) 
      : healpix::Healpix::Pixel(my_pix) {}

   double area() const {
      return healpix::Healpix::Pixel::area();
   }

   astro::SkyDir operator()() const {
      return *this;
   }

   long index() const {
      return healpix::Healpix::Pixel::index();
   }

#ifndef SWIG
   class StopIteration : public std::exception {
   public:
      StopIteration() {}
      virtual ~StopIteration() throw() {}
      virtual const char * what() const throw() {return "stop iteration";}
   };
#endif // SWIG
};

#endif // _AspHealPix_Pixel_h
