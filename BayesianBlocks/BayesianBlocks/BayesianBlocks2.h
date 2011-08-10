/**
 * @file BayesianBlocks2
 * @brief Implementation of BB algorithm for event, binned and point
 * measurement data.
 * 
 * @author J. Chiang
 *
 * $Header$
 */

#ifndef BayesianBlocks_BayesianBlocks2_h
#define BayesianBlocks_BayesianBlocks2_h

#include <deque>
#include <numeric>
#include <vector>

namespace BayesianBlocks {

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

   inline double blockSize(size_t imin, size_t imax) const {
      const_iterator_t first(m_cellSizes.begin() + imin);
      const_iterator_t last(m_cellSizes.begin() + imax + 1);
      double sum(std::accumulate(first, last, 0));
      return sum;
   }

   inline double blockContent(size_t imin, size_t imax) const {
      const_iterator_t first(m_cellContent.begin() + imin);
      const_iterator_t last(m_cellContent.begin() + imax + 1);
      double sum(std::accumulate(first, last, 0));
      return sum;
   }

   const std::vector<double> & cellContent() const {
      return m_cellContent;
   }

   const std::vector<double> & cellErrors() const {
      return m_cellErrors;
   }

private:

   bool m_point_mode;
   double m_tstart;
   std::vector<double> m_cellContent;
   std::vector<double> m_cellSizes;
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

   void ingestPointData(const std::vector<double> & xx,
                        const std::vector<double> & yy,
                        const std::vector<double> & dy);

   void lightCurve(const std::deque<size_t> & changePoints,
                   std::vector<double> & xx, 
                   std::vector<double> & yy) const;
};

} // namespace BayesianBlocks

#endif // BayesianBlocks_BayesianBlocks2_h
