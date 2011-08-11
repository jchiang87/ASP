/**
 * @file BayesianBlocks2
 * @brief Implementation of BB algorithm for event, binned and point
 * measurement data.
 * 
 * @author J. Chiang
 *
 * $Header$
 */

#ifndef _BayesianBlocks2_h
#define _BayesianBlocks2_h

#include <deque>
#include <vector>

class BayesianBlocks2 {

public:

   BayesianBlocks2(const std::vector<double> & arrival_times);

   BayesianBlocks2(double start_time, 
                   const std::vector<double> & bin_content,
                   const std::vector<double> & bin_sizes);

   BayesianBlocks2(const std::vector<double> & xx,
                   const std::vector<double> & yy,
                   const std::vector<double> & dy);

   /// @brief Compute the global optimum reconstruction of the 
   /// piecewise constant function.
   ///
   /// @param ncp_prior
   /// @param xvals abscissa values of the reconstructed function
   /// @param yvals ordinate values of the reconstructed function
   void globalOpt(double ncp_prior,
                  std::vector<double> & xvals,
                  std::vector<double> & yvals) const;

   typedef std::vector<double>::const_iterator const_iterator_t;

   double blockCost(size_t imin, size_t imax) const {
      return m_blockCost->operator()(imin, imax);
   }

   double blockSize(size_t imin, size_t imax) const;

   double blockContent(size_t imin, size_t imax) const;

   const std::vector<double> & cellContent() const {
      return m_cellContent;
   }

   const std::vector<double> & cellErrors() const {
      return m_cellErrors;
   }

   void setCellSizes(const std::vector<double> & cellSizes);

private:

   bool m_point_mode;
   bool m_binned;
   double m_tstart;
   std::vector<double> m_cellSizes;
   std::deque<double> m_unscaledCellSizePartialSums;
   std::deque<double> m_cellSizePartialSums;
   std::vector<double> m_cellContent;
   std::deque<double> m_cellContentPartialSums;
   std::vector<double> m_cellErrors;

   /// @brief Interface class for block cost functions.
   class BlockCost {
   public:

      BlockCost(const BayesianBlocks2 & bbObject) : m_bbObject(bbObject) {}

      virtual double operator()(size_t imin, size_t imax) const = 0;

   protected:

      const BayesianBlocks2 & m_bbObject;

   };

   /// @brief Cost function for unbinned or binned event-based data.
   class BlockCostEvent : public BlockCost {
   public:

      BlockCostEvent(const BayesianBlocks2 & bbObject) 
         : BlockCost(bbObject) {}

      virtual double operator()(size_t imin, size_t imax) const;

   };

   /// @brief Cost function for point measurement data.
   class BlockCostPoint : public BlockCost {
   public:

      BlockCostPoint(const BayesianBlocks2 & bbObject) 
         : BlockCost(bbObject) {}

      virtual double operator()(size_t imin, size_t imax) const;

   };

   BlockCost * m_blockCost;

   void generateCells(const std::vector<double> & arrival_times);
   void cellPartialSums();

   void ingestPointData(const std::vector<double> & xx,
                        const std::vector<double> & yy,
                        const std::vector<double> & dy);

   void lightCurve(const std::deque<size_t> & changePoints,
                   std::vector<double> & xx, 
                   std::vector<double> & yy) const;
};

#endif // _BayesianBlocks2_h
