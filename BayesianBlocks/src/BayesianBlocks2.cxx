/**
 * @file BayesianBlocks2.cxx
 * @brief Implementation of BB algorithm for event, binned and point
 * measurement data.
 * 
 * @author J. Chiang
 *
 * $Header$
 */

#include <cmath>

#include <iostream>
#include <numeric>
#include <stdexcept>

#include "BayesianBlocks/BayesianBlocks2.h"

namespace {
   void computePartialSums(const std::vector<double> & x,
                           std::deque<double> & partialSums) {
      partialSums.resize(x.size());
      std::partial_sum(x.begin(), x.end(), partialSums.begin());
      partialSums.push_front(0);
   }
}

BayesianBlocks2::
BayesianBlocks2(const std::vector<double> & arrival_times)
   : m_point_mode(false),
     m_binned(false),
     m_tstart((3*arrival_times[0] - arrival_times[1])/2.),
     m_cellSizes(arrival_times.size(), 0),
     m_cellContent(arrival_times.size(), 1.),
     m_blockCost(new BlockCostEvent(*this)) {
   generateCells(arrival_times);
}

BayesianBlocks2::
BayesianBlocks2(double tstart,
                const std::vector<double> & bin_content,
                const std::vector<double> & bin_sizes)
   : m_point_mode(false), m_binned(true), m_tstart(tstart),
     m_cellSizes(bin_sizes), m_cellContent(bin_content),
     m_blockCost(new BlockCostEvent(*this)) {
   cellPartialSums();
}

BayesianBlocks2::
BayesianBlocks2(const std::vector<double> & xx,
                const std::vector<double> & yy,
                const std::vector<double> & dy) 
   : m_point_mode(true),
     m_binned(false),
     m_tstart((3*xx[0] - xx[1])/2.),
     m_cellSizes(xx.size(), 0),
     m_cellContent(yy),
     m_cellErrors(dy),
     m_blockCost(new BlockCostPoint(*this)) {
   generateCells(xx);
}

void BayesianBlocks2::
globalOpt(double ncp_prior,
          std::vector<double> & xvals,
          std::vector<double> & yvals) const {
   std::vector<double> opt;
   std::vector<size_t> last;
   opt.push_back(blockCost(0, 0) - ncp_prior);
   last.push_back(0);
   size_t npts(m_cellContent.size());
   for (size_t nn(1); nn < npts; nn++) {
      double max_opt(blockCost(0, nn) - ncp_prior);
      size_t jmax(0);
      for (size_t j(1); j < nn+1; j++) {
         double my_opt(opt[j-1] + blockCost(j, nn) - ncp_prior);
         if (my_opt > max_opt) {
            max_opt = my_opt;
            jmax = j;
         }
      }
      opt.push_back(max_opt);
      last.push_back(jmax);
   }
   std::deque<size_t> changePoints;
   size_t indx(last.back());
   while (indx > 0) {
      changePoints.push_front(indx);
      indx = last[indx-1];
   }
   changePoints.push_front(0);
   changePoints.push_back(npts);
//    for (size_t i(0); i < changePoints.size(); i++) {
//       std::cout << changePoints[i] << "  ";
//    }
//    std::cout << std::endl;
   lightCurve(changePoints, xvals, yvals);
}

double BayesianBlocks2::blockSize(size_t imin, size_t imax) const {
   return m_cellSizePartialSums[imax+1] - m_cellSizePartialSums[imin];
}

double BayesianBlocks2::blockContent(size_t imin, size_t imax) const {
   return m_cellContentPartialSums[imax+1] - m_cellContentPartialSums[imin];
}

void BayesianBlocks2::setCellSizes(const std::vector<double> & cellSizes) {  
   if (cellSizes.size() != m_cellSizes.size()) {
      throw std::runtime_error("The number of scale factors does not equal "
                               "the number of cells.");
   }
   m_cellSizes = cellSizes;
   ::computePartialSums(m_cellSizes, m_cellSizePartialSums);
}

void BayesianBlocks2::lightCurve(const std::deque<size_t> & changePoints,
                                 std::vector<double> & xx, 
                                 std::vector<double> & yy) const {
   xx.clear();
   yy.clear();
   for (size_t i(0); i < changePoints.size() - 1; i++) {
      size_t imin(changePoints[i]);
      size_t imax(changePoints[i+1]);
      xx.push_back(m_tstart + m_unscaledCellSizePartialSums[imin]);
      xx.push_back(m_tstart + m_unscaledCellSizePartialSums[imax]);
      double yval(0);
      if (m_point_mode) {
         std::vector<double> weights;
         weights.reserve(imax - imin);
         double sum_wts(0);
         for (size_t ii(imin); ii < imax; ii++) {
            weights.push_back(1./m_cellErrors[ii]/m_cellErrors[ii]);
            sum_wts += weights.back();
            yval += weights.back()*m_cellContent[ii];
         }
         yval /= sum_wts;
      } else {
         double unscaled_block_size = 
            m_unscaledCellSizePartialSums[imax] 
            - m_unscaledCellSizePartialSums[imin];
         yval = blockContent(imin, imax-1)/unscaled_block_size;
      }
      yy.push_back(yval);
      yy.push_back(yval);
   }
}

void BayesianBlocks2::
generateCells(const std::vector<double> & arrival_times) {
   size_t npts(arrival_times.size());
   m_cellSizes[0] = arrival_times[1] - arrival_times[0];
   for (size_t i(1); i < npts-1; i++) {
      m_cellSizes[i] = (arrival_times[i+1] - arrival_times[i-1])/2.;
   }
   m_cellSizes[npts-1] = arrival_times[npts-1] - arrival_times[npts-2];
   cellPartialSums();
}

void BayesianBlocks2::cellPartialSums() {
   ::computePartialSums(m_cellSizes, m_unscaledCellSizePartialSums);
   ::computePartialSums(m_cellSizes, m_cellSizePartialSums);
   ::computePartialSums(m_cellContent, m_cellContentPartialSums);
}

double BayesianBlocks2::
BlockCostEvent::operator()(size_t imin, size_t imax) const {
   double block_size(m_bbObject.blockSize(imin, imax));
   double block_content(m_bbObject.blockContent(imin, imax));
   if (block_content == 0) {
      return 0;
   }
   double cost = block_content*(std::log(block_content/block_size) - 1.);
   return cost;
}

double BayesianBlocks2::
BlockCostPoint::operator()(size_t imin, size_t imax) const {
   std::vector<double> weights;
   weights.reserve(imax - imin);
   double sum_wts(0);
   const std::vector<double> & cellErrors(m_bbObject.cellErrors());
   for (size_t i(imin); i < imax+1; i++) {
      weights.push_back(1./cellErrors[i]/cellErrors[i]);
      sum_wts += weights.back();
   }
   double sum_wts_yy(0);
   double sigx2(0);
   size_t j(0);
   const std::vector<double> & cellContent(m_bbObject.cellContent());
   for (size_t i(imin); i < imax+1; i++, j++) {
      weights[j] /= sum_wts;
      sum_wts_yy += weights[j]*cellContent[i];
      sigx2 += weights[j]*cellContent[i]*cellContent[i];
   }
   sigx2 -= sum_wts_yy*sum_wts_yy;
   
   return -sigx2/2.*sum_wts;
}

double BayesianBlocks2::ncp_prior(double nevents, double fp_frac) {
   double value = 4. - std::log(fp_frac/(0.0136*std::pow(nevents, 0.478)));
   return value;
}
