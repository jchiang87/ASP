/**
 * @file EventClusters.cxx
 * @brief JPN and JB's photon clustering algorithm
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <cmath>

#include "CLHEP/Vector/ThreeVector.h"

#include "pyASP/EventClusters.h"

namespace pyASP {

EventClusters::
EventClusters(const std::vector< std::pair<double, double> > & gtis,
              double radius) : ClusterAlg(gtis), m_radius(radius) {}

double EventClusters::logLikePosition() const {
   const Event & largest(findLargestCluster());

   astro::SkyDir cluster_dir(meanDir(largest));

   double radius(m_radius*M_PI/180);

   double logLike(0);
   for (std::vector<Event>::const_iterator event(m_events.begin()); 
        event != m_events.end(); ++event) {
      double sep(event->dir().difference(cluster_dir));
      if (sep < radius) {
          logLike += std::log(1 - std::cos(sep));
      }
   }
   return logLike;
}

astro::SkyDir EventClusters::meanDir(const Event & event, 
                                     double radius) const {
   if (radius == 0) {
      radius = m_radius;
   }
   double xhat(0);
   double yhat(0);
   double zhat(0);
   size_t nevents(0);
   for (std::vector<Event>::const_iterator evt(m_events.begin());
        evt != m_events.end(); ++evt) {
      if (event.sep(*evt) < radius) {
         xhat += evt->dir().dir().x();
         yhat += evt->dir().dir().y();
         zhat += evt->dir().dir().z();
         nevents++;
      }
   }
   xhat /= nevents;
   yhat /= nevents;
   zhat /= nevents;
   return astro::SkyDir(CLHEP::Hep3Vector(xhat, yhat, zhat));
}

const Event & EventClusters::findLargestCluster(double radius) const {
   size_t ilargest(0);
   size_t maxSize(clusterSize(m_events.front(), radius));
   for (size_t i(1); i < m_events.size(); i++) {
      size_t currentSize(clusterSize(m_events.at(i), radius));
      if (currentSize > maxSize) {
         ilargest = i;
         maxSize = currentSize;
      }
   }
   return m_events.at(ilargest);
}

size_t EventClusters::clusterSize(const Event & event, double radius) const {
   if (radius == 0) {
      radius = m_radius;
   }
   size_t num(0);
   for (size_t j(0); j < m_events.size(); j++) {
      if (event.sep(m_events.at(j)) < radius) {
         num++;
      }
   }
   return num;
}

} // namespace pyASP
