/**
 * @file ExposureArray.h
 * @brief Subclass of HealpixArray for representing instrument exposure
 * corresponding to a CountsArray.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef _AspHealPix_ExposureArray_h
#define _AspHealPix_ExposureArray_h

#include <map>

#include "AspHealPix/HealpixArray.h"

namespace irfInterface {
   class Irfs;
}

/**
 * @class ExposureArray
 */

class ExposureArray : public HealpixArray {

public:

   ExposureArray(healpix::Healpix hp);

   ExposureArray(const std::string & infile, 
                 const std::string & extname="Exposure",
                 const std::string & fieldname="Exposure");

   ExposureArray(const HealpixArray & array);

   virtual void write(const std::string & outfile) const;

   virtual ExposureArray operator+(const ExposureArray & x) const;
   virtual ExposureArray operator-(const ExposureArray & x) const;

   void computeExposure(const std::string & irfs,
                        const std::string & livetimeCube,
                        double photonIndex=2.1, 
                        double emin=100, double emax=3e5,
                        size_t nenergies=20);

private:

   typedef std::map<int, irfInterface::Irfs *> IrfsMap_t;

   static IrfsMap_t getIrfs(const std::string & irfs);

   class Aeff {
   public:
      Aeff();
      Aeff(const IrfsMap_t & irfsMap, double energy);
      double operator()(double costheta) const;
   private:
      const IrfsMap_t * m_irfsMap;
      double m_energy;
   };

};

#endif // _AspHealPix_ExposureArray_h
