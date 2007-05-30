/**
 * @file BayesianBlocks.h
 * @author J. Chiang
 *
 * $Header$
 */

#ifndef _BayesianBlocks_h
#define _BayesianBlocks_h

#include <deque>
#include <map>
#include <string>
#include <utility>
#include <vector>

/**
 * @class BayesianBlocks
 * @brief Implementation of 1D Bayesian Blocks nominally for
 * time-tagged event data, but should be applicable to spectra,
 * substituting energies for event times.
 *
 * @author J. Chiang
 *
 * $Header$
 */

class BayesianBlocks {
   
public:

   BayesianBlocks(const std::vector<double> & eventTimes, double ncpPrior=1);
  
   BayesianBlocks(const std::vector<double> & cellContent,
                  const std::vector<double> & cellBoundaries,
                  const std::vector<double> & scaleFactors,
                  double ncpPrior=1);

   ~BayesianBlocks() throw() {}

   void computeLightCurve(std::vector<double> & tmins,
                          std::vector<double> & tmaxs,
                          std::vector<double> & numEvents);

   int setCellScaling(const std::vector<double> & scaleFactors);

   void getChangePoints(std::vector<int> & changePoints) const;

   void getCells(std::vector<double> & cells) const {
      cells = m_cells;
   }

   void getCellBoundaries(std::vector<double> & cellBoundaries, 
                          bool scaled=true) const;

   void setNcpPrior(double ncpPrior) {
      m_ncpPrior = ncpPrior;
   }

   double ncpPrior() const {
      return m_ncpPrior;
   }

   const std::vector<double> & eventTimes() const {
      return m_eventTimes;
   }

   static double gammln(double x);

private:

   bool m_binned;

   /// @brief event arrival times to be used for unbinned analysis
   std::vector<double> m_eventTimes;

   /// @brief cell counts to be used for binned mode
   std::vector<double> m_cellContent;

   std::vector<double> m_cells;
   std::vector<double> m_cellBoundaries;
   std::deque<double> m_scaledBoundaries;

   double m_ncpPrior;

   std::deque<size_t> m_changePoints;

   void createCells();

   void globalOpt();

   void renormalize();

   double blockCost(size_t imin, size_t imax) const;

   double blockSize(size_t imin, size_t imax) const;

   double blockContent(size_t imin, size_t imax) const;

   double highestBinDensity() const;

};

#endif //_BayesianBlocks_h
