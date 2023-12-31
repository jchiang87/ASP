/**
 * @file BayesianBlocks.cxx
 * @brief 1D Bayesian blocks
 * @author J. Chiang
 *
 * $Header$
 */

#include <cmath>

#include <algorithm>
#include <iostream>
#include <numeric>
#include <stdexcept>

#include "BayesianBlocks/BayesianBlocks.h"

BayesianBlocks::BayesianBlocks(const std::vector<double> & eventTimes, 
                               bool useInterval) 
   : m_binned(false), m_eventTimes(eventTimes), 
     m_cellContent(std::vector<double>(eventTimes.size(), 1)), 
     m_useInterval(useInterval) {
   if (useInterval) {
      m_cellContent.pop_back();
   }
   std::stable_sort(m_eventTimes.begin(), m_eventTimes.end());
   createCells();
}

BayesianBlocks::BayesianBlocks(const std::vector<double> & cellContent,
                               const std::vector<double> & cellBoundaries,
                               const std::vector<double> & cellExposures)
   : m_binned(true), m_cellContent(cellContent),
     m_cellSizes(cellExposures), m_cellBoundaries(cellBoundaries) {
   if (cellContent.size() != cellBoundaries.size() - 1 ||
       cellContent.size() != cellExposures.size()) {
      throw std::runtime_error("Inconsistent numbers of cells, cell "
                               "boundaries, and/or exposures.");
   }
}

void BayesianBlocks::setCellContent(const std::vector<double> & cellContent) {
   if (cellContent.size() != m_cellContent.size()) {
      throw std::runtime_error("cell content sizes do not match");
   }
   m_cellContent = cellContent;
}

void BayesianBlocks::setCellSizes(const std::vector<double> & cellSizes) {
   if (cellSizes.size() != m_cellSizes.size()) {
      throw std::runtime_error("The number of scale factors does not equal "
                               "the number of cells.");
   }
   m_cellSizes = cellSizes;
   renormalize();
}

void BayesianBlocks::computeLightCurve(double ncpPrior,
                                       std::vector<double> & tmins,
                                       std::vector<double> & tmaxs,
                                       std::vector<double> & numEvents,
                                       std::vector<double> & exposures) {
   globalOpt(ncpPrior);
   tmins.clear();
   tmaxs.clear();
   numEvents.clear();
   exposures.clear();
   for (size_t i(1); i < m_changePoints.size(); i++) {
      size_t imin = m_changePoints[i-1];
      size_t imax = m_changePoints[i];
      tmins.push_back(m_cellBoundaries[imin]);
      tmaxs.push_back(m_cellBoundaries[imax]);
      if (m_binned) {
         numEvents.push_back(blockContent(imin, imax-1));
      } else {
         numEvents.push_back(blockContent(imin, imax) - 1);
      }
      double exposure(0);
      for (size_t i(imin); i < imax; i++) {
         exposure += m_cellSizes.at(i);
      }
      exposures.push_back(exposure);
   }
}

void BayesianBlocks::getChangePoints(std::vector<int> & changePoints) const {
   changePoints.resize(m_changePoints.size());
   std::copy(m_changePoints.begin(), m_changePoints.end(), 
             changePoints.begin());
}

void BayesianBlocks::getCellBoundaries(std::vector<double> & cellBoundaries,
                                       bool scaled) const {
   if (scaled) {
      cellBoundaries.resize(m_scaledBoundaries.size());
      std::copy(m_scaledBoundaries.begin(), m_scaledBoundaries.end(),
                cellBoundaries.begin());
   } else {
      cellBoundaries = m_cellBoundaries;
   }
}

void BayesianBlocks::globalOpt(double ncpPrior) {
   std::vector<double> opt;
   opt.push_back(blockCost(0, 0) - ncpPrior);
   std::vector<size_t> last;
   last.push_back(0);
   size_t npts = m_cellContent.size();
   for (size_t nn(1); nn < npts; nn++) {
      double max_opt = blockCost(0, nn) - ncpPrior;
      size_t jmax(0);
      for (size_t j(1); j < nn+1; j++) {
         double my_opt = opt[j-1] + blockCost(j, nn) - ncpPrior;
         if (my_opt > max_opt) {
            max_opt = my_opt;
            jmax = j;
         }
      }
      opt.push_back(max_opt);
      last.push_back(jmax);
   }
   m_changePoints.clear();
   size_t indx = last[npts-1];
   while (indx > 0) {
      m_changePoints.push_front(indx);
      indx = last[indx-1];
   }
   m_changePoints.push_front(0);
   m_changePoints.push_back(npts);
//    for (size_t i(0); i < m_changePoints.size(); i++) {
//       std::cout << m_changePoints[i] << "  ";
//    }
//    std::cout << std::endl;
}

void BayesianBlocks::createCells() {
   size_t npts = m_eventTimes.size();
   if (m_useInterval) {
      m_cellBoundaries = m_eventTimes;
      npts--;
   } else {
      m_cellBoundaries.clear();
      m_cellBoundaries.push_back((3.*m_eventTimes[0] - m_eventTimes[1])/2.);
      for (size_t i(1); i < npts; i++) {
         m_cellBoundaries.push_back((m_eventTimes[i-1] + m_eventTimes[i])/2.);
      }
      m_cellBoundaries.push_back((3.*m_eventTimes[npts-1] 
                                  - m_eventTimes[npts-2])/2.);
   }
   m_cellSizes.clear();
   for (size_t i(0); i < npts; i++) {
      m_cellSizes.push_back(m_cellBoundaries[i+1] - m_cellBoundaries[i]);
   }
   renormalize();
}

void BayesianBlocks::renormalize() {
   m_scaledBoundaries.resize(m_cellSizes.size());
   std::partial_sum(m_cellSizes.begin(), m_cellSizes.end(), 
                    m_scaledBoundaries.begin());
   m_scaledBoundaries.push_front(0);
}

double BayesianBlocks::blockCost(size_t imin, size_t imax) const {
   double size(blockSize(imin, imax));
   double content(blockContent(imin, imax));
   if (::getenv("USE_POSTERIOR_COST")) {
      double arg = size - content;
      if (arg > 0) {
         return gammln(content + 1.) + gammln(arg + 1.) - gammln(size + 2.);
      }
      return -log(size);
   }
   return content*(std::log(content) - std::log(size));
}

double BayesianBlocks::blockSize(size_t imin, size_t imax) const {
   return m_scaledBoundaries[imax+1] - m_scaledBoundaries[imin];
}

double BayesianBlocks::blockContent(size_t imin, size_t imax) const {
   double content(0);
   if (m_binned) {
      for (size_t i(imin); i < imax+1; i++) {
         if (i < m_cellContent.size()) {
            content += m_cellContent.at(i);
         }
      }
   } else {
       content = imax - imin + 1.;
   }
   return content;
}

double BayesianBlocks::gammln(double xx) {
   static double cof[6] = {76.18009172947146, -86.50532032941677,
                           24.01409824083091, -1.231739572450155,
                           0.1208650973866179e-2, -0.5395239384953e-5};
   double y = xx;
   double x = xx;
   double tmp = x + 5.5;
   tmp -= (x + 0.5)*log(tmp);
   double ser = 1.000000000190015;
   for (int j = 0; j < 6; j++) {
      ser += cof[j]/++y;
   }
   return -tmp + log(2.5066282746310005*ser/x);
}
