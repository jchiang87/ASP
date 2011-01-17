/**
 * @file Exposure.cxx
 * @brief LAT effective area, integrated over time bins.
 * @author J. Chiang
 *
 * $Header$
 */

#include <algorithm>
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
   m_scData->readData(scFiles, m_timeBoundaries.front(), 
                      m_timeBoundaries.back());
}

void Exposure::integrateExposure() {
   m_exposureValues.resize(m_timeBoundaries.size() - 1);
   for (size_t j(0); j < m_exposureValues.size(); j++) {
      m_exposureValues.at(j) = 0;
      std::pair<double, double> wholeInterval;
      wholeInterval.first = m_timeBoundaries.at(j);
      wholeInterval.second = m_timeBoundaries.at(j+1);

      size_t imin, imax;
      try {
         imin = m_scData->time_index(m_timeBoundaries.at(j));
         imax = m_scData->time_index(m_timeBoundaries.at(j+1)) + 1;
      } catch (std::runtime_error &) {
         imin = 0;
         imax = m_scData->numIntervals() - 1;
      }
      imax = std::min(imax, m_scData->numIntervals() - 1);
      for (size_t i(imin); i < imax + 1; i++) {
         double tstart(m_scData->start(i));
         double tstop(m_scData->stop(i));
         std::pair<double, double> thisInterval;
         thisInterval.first = tstart;
         thisInterval.second = tstop;
         double overlap = 
            Likelihood::LikeExposure::overlap(wholeInterval, thisInterval);
         if (overlap) {
            m_exposureValues.at(j) += ((effArea(thisInterval.first) 
                                        + effArea(thisInterval.second))/2.
                                       *overlap);
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
