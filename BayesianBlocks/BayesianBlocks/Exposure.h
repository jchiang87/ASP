/**
 * @file Exposure
 * @brief LAT effective area, integrated over time bins, to a specific
 * point on the sky.
 * @author J. Chiang
 *
 * $Header$
 */

#ifndef _Exposure_h
#define _Exposure_h

#include <string>
#include <vector>

#include "astro/SkyDir.h"

namespace irfInterface {
   class Irfs;
}

namespace Likelihood {
   class ScData;
}

/**
 * @class Exposure
 * @brief LAT effective area, integrated over time bins, to a specific
 * point on the sky.
 *
 * @author J. Chiang
 *
 * $Header$
 */

class Exposure {

public:

   Exposure(const std::string & scDataFile, 
            const std::vector<double> &timeBoundaries,
            double ra, double dec,
            const std::string & frontIrfs="testIrfs::Front",
            const std::string & backIrfs="testIrfs::Back");

   ~Exposure() throw();

   double value(double time) const;

   double photonEnergy() const {return m_energy;}
   void setPhotonEnergy(double energy) {m_energy = energy;}

private:

   std::vector<double> m_timeBoundaries;
   irfInterface::Irfs * m_irfs_front;
   irfInterface::Irfs * m_irfs_back;
   double m_energy;
   astro::SkyDir m_srcDir;
   std::vector<double> m_exposureValues;

   Likelihood::ScData * m_scData;

   void readScData(const std::string & filename);
   void integrateExposure();
   double effArea(double time) const;
};

#endif // _Exposure_h
