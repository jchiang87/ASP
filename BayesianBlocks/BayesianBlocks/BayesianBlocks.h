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
 */

class BayesianBlocks {
   
public:

   BayesianBlocks(const std::vector<double> & eventTimes,
                  bool useInterval=false);
  
   BayesianBlocks(const std::vector<double> & cellContent,
                  const std::vector<double> & cellBoundaries,
                  const std::vector<double> & cellExposures);

   ~BayesianBlocks() throw() {}

   void setCellContent(const std::vector<double> & cellContent);

   void setCellSizes(const std::vector<double> & cellSizes);

   void computeLightCurve(double ncpPrior,
                          std::vector<double> & tmins,
                          std::vector<double> & tmaxs,
                          std::vector<double> & numEvents,
                          std::vector<double> & exposures);

   void getChangePoints(std::vector<int> & changePoints) const;

   void getCellSizes(std::vector<double> & cellSizes) const {
      cellSizes = m_cellSizes;
   }

   void getCellBoundaries(std::vector<double> & cellBoundaries, 
                          bool scaled=false) const;

   const std::vector<double> & eventTimes() const {
      return m_eventTimes;
   }

   static double gammln(double x);

private:

   bool m_binned;

   /// Event arrival times to be used for unbinned analysis
   std::vector<double> m_eventTimes;

   /// Cell counts to be used for binned mode
   std::vector<double> m_cellContent;

   /// Size of cells (proportional to duration or exposure)
   std::vector<double> m_cellSizes;

   /// Cell boundaries in unscaled units
   std::vector<double> m_cellBoundaries;

   /// Cell boundaries in scaled (i.e., exposure-weighted) units
   std::deque<double> m_scaledBoundaries;

   bool m_useInterval;

   std::deque<size_t> m_changePoints;

   void createCells();

   void globalOpt(double ncpPrior);

   void renormalize();

   double blockCost(size_t imin, size_t imax) const;

   double blockSize(size_t imin, size_t imax) const;

   double blockContent(size_t imin, size_t imax) const;

//   double highestBinDensity() const;

};

#endif //_BayesianBlocks_h
