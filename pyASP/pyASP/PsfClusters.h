/**
 * @file PsfClusters.h
 * @brief Photon cluster detection algorithm using the PSF
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef pyASP_PsfClusters_h
#define pyASP_PsfClusters_h

#include <map>

#include "pyASP/ClusterAlg.h"

#include "pyASP/ScData.h"

namespace irfInterface {
   class IPsf;
}

namespace pyASP {

class ScData;

/**
 * @class PsfClusters
 */

class PsfClusters : public ClusterAlg {

public:

   PsfClusters(const std::vector< std::pair<double, double> > & gtis,
               const ScData & scData,
               const std::string & irfs="DC2");

   virtual ~PsfClusters();

   virtual void process(const std::vector<Event> & events,
                        double & logLike_time, double & logLike_pos,
                        astro::SkyDir & meanDir, double bg_rate=0);

private:
   
   const ScData & m_scData;

   double m_logLikePosition;

   astro::SkyDir m_clusterDir;

   std::map<size_t, irfInterface::IPsf *> m_psfs;

   void process();

   const irfInterface::IPsf & psf(size_t item) const;

   const Event & findLargestCluster(double & logLike) const;
   void computePsfWts(const Event & evt, std::map<Event, double> & wts) const;
   double eventLogLike(const Event & evt) const;
   double eventLogLike(const std::map<Event, double> & wts) const;

   void loadIrfs(const std::string & irfs);

};

} // namespace pyASP

#endif // pyASP_PsfClusters_h
