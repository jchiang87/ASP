/**
 * @file Exposure.cxx
 * @brief LAT effective area, integrated over time bins.
 * @author J. Chiang
 *
 * $Header$
 */

#include <stdexcept>
#include <utility>

#include "st_facilities/Util.h"

#include "irfInterface/IrfsFactory.h"
#include "irfLoader/Loader.h"

#include "Likelihood/LikeExposure.h"
#include "Likelihood/ScData.h"

#include "BayesianBlocks/Exposure.h"

Exposure::Exposure(const std::string & scDataFile,
                   const std::vector<double> & timeBoundaries,
                   double ra, double dec, const std::string & frontIrfs,
                   const std::string & backIrfs) 
   : m_timeBoundaries(timeBoundaries), m_irfs_front(0), m_irfs_back(0), 
     m_energy(300.), m_scData(0) {
   m_srcDir = astro::SkyDir(ra, dec);
   irfLoader::Loader::go();
   m_irfs_front = irfInterface::IrfsFactory::instance()->create(frontIrfs);
   m_irfs_back = irfInterface::IrfsFactory::instance()->create(backIrfs);
   m_scData = new Likelihood::ScData();
   readScData(scDataFile);
   integrateExposure();
}

Exposure::~Exposure() throw() {
   delete m_scData;
   delete m_irfs_front;
   delete m_irfs_back;
}
   
double Exposure::value(double time) const {
   int indx = std::upper_bound(m_timeBoundaries.begin(), 
                               m_timeBoundaries.end(), time) 
      - m_timeBoundaries.begin() - 1;
   return m_exposureValues[indx];
}

void Exposure::readScData(const std::string & scDataFile) {
   std::vector<std::string> scFiles;
   st_facilities::Util::resolve_fits_files(scDataFile, scFiles);
   std::vector<std::string>::const_iterator scIt = scFiles.begin();
   bool clear(true);
   for ( ; scIt != scFiles.end(); scIt++) {
      st_facilities::Util::file_ok(*scIt);
      m_scData->readData(*scIt, clear);
      clear = false;
   }
}

void Exposure::integrateExposure() {
   unsigned int numIntervals = m_timeBoundaries.size() - 1;
   m_exposureValues.resize(numIntervals);
   for (unsigned int i = 0; i < numIntervals; i++) {
      m_exposureValues[i] = 0;
      std::pair<double, double> wholeInterval;
      wholeInterval.first = m_timeBoundaries[i];
      wholeInterval.second = m_timeBoundaries[i+1];
      std::pair<Likelihood::ScData::Iterator, 
         Likelihood::ScData::Iterator> scData;
      Likelihood::ScData::Iterator firstIt = m_scData->vec.begin();
      Likelihood::ScData::Iterator lastIt = m_scData->vec.end() - 1;
      try {
         scData = m_scData->bracketInterval(wholeInterval);
         if (scData.first - firstIt < 0) scData.first = firstIt;
         if (scData.second - firstIt > lastIt - firstIt) 
            scData.second = lastIt;
      } catch (std::out_of_range &eObj) { // use brute force
         scData = std::make_pair(firstIt, lastIt);
      }
      for (Likelihood::ScData::Iterator it = scData.first; 
           it != (scData.second-1); ++it) {
         std::pair<double, double> thisInterval;
         thisInterval.first = it->time;
         thisInterval.second = (it+1)->time;
         if (Likelihood::LikeExposure::overlap(wholeInterval, thisInterval)) {
            m_exposureValues[i] += (effArea(thisInterval.first) 
                                    + effArea(thisInterval.second))/2.
               *(thisInterval.second - thisInterval.first);
         }
      }
   }
}

double Exposure::effArea(double time) const {
   astro::SkyDir zAxis = m_scData->zAxis(time);
   astro::SkyDir xAxis = m_scData->xAxis(time);
   
   irfInterface::IAeff * aeff_front = m_irfs_front->aeff();
   irfInterface::IAeff * aeff_back = m_irfs_back->aeff();
   return aeff_front->value(m_energy, m_srcDir, zAxis, xAxis)
      + aeff_back->value(m_energy, m_srcDir, zAxis, xAxis);
}
