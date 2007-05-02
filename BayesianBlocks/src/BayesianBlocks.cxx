/**
 * @file BayesianBlocks.cxx
 * @brief 1D Bayesian blocks
 * @author J. Chiang
 *
 * $Header$
 */

#include <cmath>

#include <iostream>
#include <numeric>
#include <stdexcept>

#include "BayesianBlocks/BayesianBlocks.h"

BayesianBlocks::BayesianBlocks(const std::vector<double> & eventTimes, 
                               double ncpPrior) 
   : m_binned(false), m_eventTimes(eventTimes), 
     m_cellContent(std::vector<double>(eventTimes.size(), 1)), 
     m_ncpPrior(ncpPrior) {
   std::stable_sort(m_eventTimes.begin(), m_eventTimes.end());
   createCells();
}

BayesianBlocks::BayesianBlocks(const std::vector<double> & cellContent,
                               const std::vector<double> & cellBoundaries,
                               const std::vector<double> & scaleFactors,
                               double ncpPrior) 
   : m_binned(true), m_cellContent(cellContent), 
     m_cellBoundaries(cellBoundaries), m_ncpPrior(ncpPrior) {
   if (cellContent.size() != cellBoundaries.size() - 1 ||
       cellContent.size() != scaleFactors.size()) {
      throw std::runtime_error("Inconsistent numbers of cells, cell "
                               "boundaries, and/or scale factors.");
   }
   setCellScaling(scaleFactors);
}

int BayesianBlocks::setCellScaling(const std::vector<double> & scaleFactors) {
   if (scaleFactors.size() == m_cells.size()) {
      for (unsigned int i = 0; i < scaleFactors.size(); i++) {
         m_cells[i] *= scaleFactors[i];
      }
      renormalize();
      return 1;
   }
   return 0;
}

void BayesianBlocks::computeLightCurve(std::vector<double> & tmins,
                                       std::vector<double> & tmaxs,
                                       std::vector<double> & numEvents) {
   globalOpt();
   tmins.clear();
   tmaxs.clear();
   numEvents.clear();
   for (unsigned int i = 1; i < m_changePoints.size(); i++) {
      unsigned int imin = m_changePoints[i-1];
      unsigned int imax = m_changePoints[i];
      tmins.push_back(m_cellBoundaries[imin]);
      tmaxs.push_back(m_cellBoundaries[imax]);
      numEvents.push_back(blockContent(imin, imax));
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

void BayesianBlocks::globalOpt() {
   std::vector<double> opt;
   opt.push_back(blockCost(0, 0) - m_ncpPrior);
   std::vector<unsigned int> last;
   last.push_back(0);
   unsigned int npts = m_eventTimes.size();
   for (unsigned int nn = 1; nn < npts; nn++) {
      double max_opt = blockCost(0, nn) - m_ncpPrior;
      unsigned int jmax(0);
      for (unsigned int j = 1; j < nn+1; j++) {
         double my_opt = opt[j-1] + blockCost(j, nn) - m_ncpPrior;
         if (my_opt > max_opt) {
            max_opt = my_opt;
            jmax = j;
         }
      }
      opt.push_back(max_opt);
      last.push_back(jmax);
   }
   m_changePoints.clear();
   unsigned int indx = last[npts-1];
   while (indx > 0) {
      m_changePoints.push_front(indx);
      indx = last[indx-1];
   }
   m_changePoints.push_front(0);
   m_changePoints.push_back(npts);
}

void BayesianBlocks::createCells() {
   unsigned int npts = m_eventTimes.size();
   m_cellBoundaries.clear();
   m_cellBoundaries.push_back((3.*m_eventTimes[0] - m_eventTimes[1])/2.);
   for (unsigned int i = 1; i < npts; i++) {
      m_cellBoundaries.push_back((m_eventTimes[i-1] + m_eventTimes[i])/2.);
   }
   m_cellBoundaries.push_back((3.*m_eventTimes[npts-1] 
                               - m_eventTimes[npts-2])/2.);
   m_cells.clear();
   for (unsigned int i = 0; i < npts; i++) {
      m_cells.push_back(std::fabs(m_cellBoundaries[i] 
                                  - m_cellBoundaries[i+1]));
   }
   renormalize();
}

void BayesianBlocks::renormalize() {
   double smallest_cell(1./highestBinDensity());
//    if (m_binned) {
//       smallest_cell = 1./highestBinDensity();
//    } else {
//       smallest_cell = m_eventTimes.back() - m_eventTimes.front();
//       for (unsigned int i = 0; i < m_cells.size(); i++) {
//          if (m_cells[i] < smallest_cell && m_cells[i] > 0) {
//             smallest_cell = m_cells[i];
//          }
//       }
//    }
   std::transform(m_cells.begin(), m_cells.end(), m_cells.begin(), 
                  std::bind2nd(std::multiplies<double>(), 2./smallest_cell));
   m_scaledBoundaries.resize(m_cells.size());
   std::partial_sum(m_cells.begin(), m_cells.end(), 
                    m_scaledBoundaries.begin());
   m_scaledBoundaries.push_front(0);
}

double BayesianBlocks::highestBinDensity() const {
   double maxDensity(m_cellContent.front()
                     /(m_cellBoundaries.at(1) - m_cellBoundaries.front()));
   for (size_t i(1); i < m_cellContent.size(); i++) {
      double density(m_cellContent.at(i)
                     /(m_cellBoundaries.at(i+1) - m_cellBoundaries.at(i)));
      if (density > maxDensity) {
         maxDensity = density;
      }
   }
   return maxDensity;
}

double BayesianBlocks::blockCost(unsigned int imin, unsigned int imax) const {
   double size = blockSize(imin, imax);
   double content = blockContent(imin, imax);
   double arg = size - content;
   if (arg > 0) {
      double my_cost = gammln(content + 1.) + gammln(arg + 1.) 
         - gammln(size + 2.);
      return my_cost;
   }
   return -log(size);
}

double BayesianBlocks::blockSize(unsigned int imin, unsigned int imax) const {
   return m_scaledBoundaries[imax+1] - m_scaledBoundaries[imin];
}

double BayesianBlocks::blockContent(unsigned int imin, 
                                    unsigned int imax) const {
   if (m_binned) {
      double content(0);
      for (size_t i(imin); i < imax+1; i++) {
         content += m_cellContent.at(i);
      }
      return content;
   }
   return imax - imin + 1.;
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
