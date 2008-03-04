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
  
   BayesianBlocks(const std::vector<double> & eventTimes, double ncpPrior=1.);
   
//    BayesianBlocks(const std::string & filename, double ncpPrior=1.);

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

   void setNcpPrior(double ncpPrior) {m_ncpPrior = ncpPrior;}

   double ncpPrior() const {return m_ncpPrior;}

   static double gammln(double x);

private:

   std::vector<double> m_eventTimes;

   double m_ncpPrior;

   std::vector<double> m_cells;
   std::vector<double> m_cellBoundaries;
   std::deque<double> m_scaledBoundaries;

   std::deque<unsigned int> m_changePoints;

   void createCells();

   void globalOpt();

   void renormalize();

   double blockCost(unsigned int imin, unsigned int imax) const;

   double blockSize(unsigned int imin, unsigned int imax) const;

   double blockContent(unsigned int imin, unsigned int imax) const;

};

#endif //_BayesianBlocks_h
