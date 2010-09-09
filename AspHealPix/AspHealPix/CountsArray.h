/**
 * @file CountsArray.h
 * @brief Subclass of HealpixArray for representing binned counts on 
 * the sky.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef _AspHealPix_CountsArray_h
#define _AspHealPix_CountsArray_h

#include "AspHealPix/HealpixArray.h"

/**
 * @class CountsArray
 */

class CountsArray : public HealpixArray {

public:

   CountsArray(healpix::Healpix hp);

   CountsArray(const std::string & infile, 
               const std::string & extname="binned_counts",
               const std::string & fieldname="counts");

   CountsArray(const HealpixArray & array);

   virtual void write(const std::string & outfile) const;

   virtual CountsArray operator+(const CountsArray & x) const;
   virtual CountsArray operator-(const CountsArray & x) const;

   void binCounts(const std::string & ft1file, 
                  const std::string & filter="");

};

#endif // _AspHealPix_CountsArray_h
