/**
 * @file ClusterAlg.h
 * @brief Base class for clustering algorithms for LAT event data.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 * 
 * $Header$
 */

#ifndef grbASP_ClusterAlg_h
#define grbASP_ClusterAlg_h

#include <utility>
#include <vector>

#include "grbASP/Event.h"

namespace grbASP {

/**
 * @class ClusterAlg
 */

class ClusterAlg {

public:

   ClusterAlg(const std::vector< std::pair<double, double> > & gtis);

   virtual ~ClusterAlg() {}

   virtual void process(const std::vector<Event> & events,
                        double & logLike_time, double & logLike_pos,
                        astro::SkyDir & meanDir, double bg_rate=0,
                        double radius=10) {
      m_events = events;
      logLike_time = logLikeTime(bg_rate);
      logLike_pos = logLikePosition();
      meanDir = clusterDir(radius);
   }

protected:

   std::vector< std::pair<double, double> > m_gtis;

   std::vector<Event> m_events;

   virtual double logLikeTime(double bg_rate) const;
   
   virtual double logLikePosition() const {
      return 0;
   }

   virtual astro::SkyDir clusterDir(double radius=10) const {
      (void)(radius);
      return astro::SkyDir(0, 0);
   };

private:

   typedef std::vector< std::pair<double, double> >::const_iterator 
           GtiIterator_t;

   double goodTime(double tmin, double tmax) const {
      GtiIterator_t first, last;
      getGtis(tmin, tmax, first, last);
      return goodTime(tmin, tmax, first, last);
   }

   double goodTime(double tmin, double tmax, 
                   GtiIterator_t first, GtiIterator_t last) const;

   void getGtis(double tmin, double tmax, 
                GtiIterator_t & first, GtiIterator_t & last) const;

};

} // namespace grbASP 

#endif // grbASP_ClusterAlg_h
