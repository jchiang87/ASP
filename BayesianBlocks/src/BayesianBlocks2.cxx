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

#include <algorithm>
#include <iostream>
#include <numeric>

#include "BayesianBlocks/BayesianBlocks2.h"

BayesianBlocks2::
BayesianBlocks2(const std::vector<double> & arrival_times)
   : m_point_mode(false),
     m_binned(false),
     m_tstart((3*arrival_times[0] - arrival_times[1])/2.),
     m_cellContent(arrival_times.size(), 1.),
     m_cellSizes(arrival_times.size(), 0),
     m_blockCost(new BlockCostEvent(*this)) {
   generateCells(arrival_times);
   rescaleCells();
}

BayesianBlocks2::
BayesianBlocks2(double tstart,
                const std::vector<double> & bin_content,
                const std::vector<double> & bin_sizes)
   : m_point_mode(false), m_binned(true), m_tstart(tstart),
     m_cellContent(bin_content), m_cellSizes(bin_sizes),
     m_blockCost(new BlockCostEvent(*this)) {
   rescaleCells();
}

BayesianBlocks2::
BayesianBlocks2(const std::vector<double> & xx,
                const std::vector<double> & yy,
                const std::vector<double> & dy) 
   : m_point_mode(true),
     m_binned(false),
     m_tstart((3*xx[0] - xx[1])/2.),
     m_cellContent(yy),
     m_cellSizes(xx.size(), 0),
     m_cellErrors(dy),
     m_blockCost(new BlockCostPoint(*this)),
     m_cellScale(1) {
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
   for (size_t i(0); i < changePoints.size(); i++) {
      std::cout << changePoints[i] << "  ";
   }
   lightCurve(changePoints, xvals, yvals);
}

double BayesianBlocks2::blockSize(size_t imin, size_t imax) const {
   const_iterator_t first(m_cellSizes.begin() + imin);
   const_iterator_t last(m_cellSizes.begin() + imax + 1);
   double sum(0);
   sum = std::accumulate(first, last, sum);
   return sum;
}

double BayesianBlocks2::blockContent(size_t imin, size_t imax) const {
   const_iterator_t first(m_cellContent.begin() + imin);
   const_iterator_t last(m_cellContent.begin() + imax + 1);
   double sum(0);
   sum = std::accumulate(first, last, sum);
   return sum;
}

void BayesianBlocks2::lightCurve(const std::deque<size_t> & changePoints,
                                 std::vector<double> & xx, 
                                 std::vector<double> & yy) const {
   std::vector<double> cellSizes(m_cellSizes.size());
   for (size_t i(0); i < m_cellSizes.size(); i++) {
      cellSizes[i] = m_cellSizes[i]/m_cellScale;
   }
   std::deque<double> sizeIntegrals(cellSizes.size());
   std::partial_sum(cellSizes.begin(), cellSizes.end(), 
                    sizeIntegrals.begin());
   sizeIntegrals.push_front(0);

   std::deque<double> contentIntegrals(m_cellContent.size());
   std::partial_sum(m_cellContent.begin(), m_cellContent.end(), 
                    contentIntegrals.begin());
   contentIntegrals.push_front(0);

   xx.clear();
   yy.clear();
   for (size_t i(0); i < changePoints.size() - 1; i++) {
      size_t imin(changePoints[i]);
      size_t imax(changePoints[i+1]);
      xx.push_back(m_tstart + sizeIntegrals[imin]);
      xx.push_back(m_tstart + sizeIntegrals[imax]);
      double yval(0);
      if (m_point_mode) {
         std::vector<double> weights;
         weights.reserve(imax - imin);
         double sum_one_over_sig2(0);
         double yval(0);
         for (size_t ii(imin); ii < imax+1; ii++) {
            weights.push_back(1./m_cellErrors[ii]/m_cellErrors[ii]);
            sum_one_over_sig2 += weights.back();
            yval += weights.back()*m_cellContent[ii];
         }
         yval /= sum_one_over_sig2;
      } else {
         const_iterator_t begin = m_cellContent.begin() + imin;
         const_iterator_t end = m_cellContent.begin() + imax;
         yval = ((contentIntegrals[imax] - contentIntegrals[imin])/
                 (sizeIntegrals[imax] - sizeIntegrals[imin])); 
      }
      yy.push_back(yval);
      yy.push_back(yval);
   }
}

void BayesianBlocks2::
generateCells(const std::vector<double> & arrival_times) {
   size_t npts(arrival_times.size());
   m_cellSizes[0] = arrival_times[1] - arrival_times[0];
   for (size_t i(1); i < arrival_times.size()-1; i++) {
      m_cellSizes[i] = (arrival_times[i+1] - arrival_times[i-1])/2.;
   }
   m_cellSizes[npts-1] = arrival_times[npts-1] - arrival_times[npts-2];
}

void BayesianBlocks2::rescaleCells() {
   double smallest_cell(m_cellSizes.front());
   for (size_t i(1); i < m_cellSizes.size(); i++) {
      if (smallest_cell > m_cellSizes[i]) {
         smallest_cell = m_cellSizes[i];
      }
   }
   m_cellScale = 2./smallest_cell;
   if (m_binned) {
      double zero(0);
      m_cellScale *= std::accumulate(m_cellContent.begin(), 
                                     m_cellContent.end(), zero);
   }
   for (size_t i(0); i < m_cellSizes.size(); i++) {
      m_cellSizes[i] *= m_cellScale;
   }
}

double BayesianBlocks2::
BlockCostEvent::operator()(size_t imin, size_t imax) const {
   double block_size(m_bbObject.blockSize(imin, imax));
   double block_content(m_bbObject.blockContent(imin, imax));
   double arg(block_size - block_content);
   if (arg > 0) {
      double cost = block_content*(std::log(block_content/block_size) - 1.);
      return cost;
   }
   return -std::log(block_size);
}

double BayesianBlocks2::
BlockCostPoint::operator()(size_t imin, size_t imax) const {
   std::vector<double> weights;
   weights.reserve(imax - imin);
   double sum_one_over_sig2(0);
   const std::vector<double> & cellErrors(m_bbObject.cellErrors());
   for (size_t i(imin); i < imax+1; i++) {
      weights.push_back(1./cellErrors[i]/cellErrors[i]);
      sum_one_over_sig2 += weights.back();
   }
   double sum_wts_yy(0);
   double sigx2(0);
   size_t j(0);
   const std::vector<double> & cellContent(m_bbObject.cellContent());
   for (size_t i(imin); i < imax+1; i++, j++) {
      weights[j] /= sum_one_over_sig2;
      sum_wts_yy += weights[j]*cellContent[i];
      sigx2 += weights[j]*cellContent[i]*cellContent[i];
   }
   sigx2 -= sum_wts_yy*sum_wts_yy;
   
   return -sigx2/2.*sum_one_over_sig2;
}
