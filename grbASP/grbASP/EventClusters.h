/**
 * @file EventClusters.h
 * @brief JPN and JB's photon clustering algorithm
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef grbASP_EventClusters_h
#define grbASP_EventClusters_h

#include "grbASP/ClusterAlg.h"

namespace grbASP {

/**
 * @class EventClusters
 */

class EventClusters : public ClusterAlg {

public:

   EventClusters(const std::vector< std::pair<double, double> > & gtis,
                 double radius=17);

   virtual ~EventClusters() {}

protected:

   virtual double logLikePosition() const;

   virtual astro::SkyDir clusterDir(double radius) const {
      return meanDir(findLargestCluster(radius), radius);
   }

private:

   double m_radius;

   const Event & findLargestCluster(double radius=0) const;

   astro::SkyDir meanDir(const Event & event, double radius=0) const;

   size_t clusterSize(const Event & event, double radius=0) const;

};

} // namespace grbASP

#endif // grbASP_EventClusters_h
