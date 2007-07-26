/**
 * @file ClusterAlg.cxx
 * @brief Base class for clustering algorithms for LAT event data.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <cmath>

#include <algorithm>
#include <iostream>

#include "grbASP/ClusterAlg.h"

namespace {
// These should always return bracketing intervals, since the aa
// arguments are first and last event times that are assumed to have
// been filtered by the GTIs we are considering.
   bool bracket_first(const std::pair<double, double> & aa,
                      const std::pair<double, double> & bb) {
      return aa.first < bb.second;
   }
   bool bracket_second(const std::pair<double, double> & aa,
                      const std::pair<double, double> & bb) {
      return aa.second < bb.second;
   }
}

namespace grbASP {

ClusterAlg::ClusterAlg(const std::vector< std::pair<double, double> > & gtis)
   : m_gtis(gtis) {}

double ClusterAlg::logLikeTime(double bg_rate) const {
   std::vector<double> times;
   for (std::vector<Event>::const_iterator event = m_events.begin();
        event != m_events.end(); ++event) {
      times.push_back(event->time());
   }

   std::stable_sort(times.begin(), times.end());

   GtiIterator_t first, last;
   getGtis(times.front(), times.back(), first, last);

   if (bg_rate == 0) {
      bg_rate = times.size()/goodTime(times.front(), times.back(), 
                                      first, last);
   }
   
   double logLike(0);
   for (size_t j(1); j < times.size(); j++) {
      double dt(times.at(j) - times.at(j-1));
      if (first != last) {
         dt = goodTime(times.at(j-1), times.at(j));
      }
      double xval(bg_rate*dt);
      logLike += std::log(1. - std::exp(-xval));
   }
   return logLike;
}

double ClusterAlg::goodTime(double tmin, double tmax,
                            GtiIterator_t start, GtiIterator_t stop) const {
   if (start == stop) {
      return tmax - tmin;
   }

   double total((start->second - tmin) + (tmax - stop->first));
   
   for (GtiIterator_t interval(start + 1); interval != stop; ++interval) {
      total += (interval->second - interval->first);
   }

   return total;
}

void ClusterAlg::getGtis(double tmin, double tmax, 
                         GtiIterator_t & first, GtiIterator_t & last) const {
   std::pair<double, double> target(tmin, tmax);
   first = std::upper_bound(m_gtis.begin(), m_gtis.end(), target,
                            ::bracket_first);
   last = std::upper_bound(m_gtis.begin(), m_gtis.end(), target,
                           ::bracket_second);
}

} // namespace grbASP
