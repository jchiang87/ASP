/**
 * @file PsfClusters.cxx
 * @brief Photon cluster detection algorithm using the PSF
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <iostream>
#include <sstream>
#include <stdexcept>
#include <utility>

#include "irfInterface/IrfsFactory.h"
#include "irfInterface/IPsf.h"

#include "irfLoader/Loader.h"

#include "grbASP/PsfClusters.h"
#include "grbASP/ScData.h"

namespace grbASP {

PsfClusters::PsfClusters(const std::vector< std::pair<double, double> > & gtis,
                         const ScData & scData,
                         const std::string & irfs) 
   : ClusterAlg(gtis), m_scData(scData) {
   loadIrfs(irfs);
}

void PsfClusters::process(const std::vector<Event> & events,
                          double & logLike_time, double & logLike_pos,
                          astro::SkyDir & meanDir, double bg_rate) {
   m_events = events;
   logLike_time = logLikeTime(bg_rate);

   std::map<Event, double> wts;
   const Event & largest(findLargestCluster(logLike_pos));
   logLike_pos *= -1;
   computePsfWts(largest, wts);
   double xhat(0);
   double yhat(0);
   double zhat(0);
   double norm(0);
   for (std::map<Event, double>::const_iterator wt(wts.begin());
        wt != wts.end(); ++wt) {
      xhat += wt->first.dir().dir().x()*wt->second;
      yhat += wt->first.dir().dir().y()*wt->second;
      zhat += wt->first.dir().dir().z()*wt->second;
      norm += wt->second;
   }
   xhat /= norm;
   yhat /= norm;
   zhat /= norm;
   meanDir = astro::SkyDir(CLHEP::Hep3Vector(xhat, yhat, zhat));
}

PsfClusters::~PsfClusters() {
   for (std::map<size_t, irfInterface::IPsf *>::iterator item(m_psfs.begin());
        item != m_psfs.end(); ++item) {
      delete item->second;
      item->second = 0;
   }
}

double PsfClusters::eventLogLike(const Event & evt) const {
   std::map<Event, double> wts;
   computePsfWts(evt, wts);
   return eventLogLike(wts);
}

double PsfClusters::eventLogLike(const std::map<Event, double> & wts) const {
   double logLike(0);
   for (std::map<Event, double>::const_iterator wt(wts.begin());
        wt != wts.end(); ++wt) {
      logLike += std::log(wt->second);
   }
   return logLike;
}

const Event & PsfClusters::findLargestCluster(double & maxLogLike) const {
   size_t ilargest(0);
   maxLogLike = eventLogLike(m_events.front());
   for (size_t i(1); i < m_events.size(); i++) {
      double currentLogLike(eventLogLike(m_events.at(i)));
      if (currentLogLike > maxLogLike) {
         ilargest = i;
         maxLogLike = currentLogLike;
      }
   }
   return m_events.at(ilargest);
}

void PsfClusters::computePsfWts(const Event & evt, 
                                std::map<Event, double> & wts) const {
   wts.clear();
   double theta(m_scData.inclination(evt.time(), evt.dir()));
   std::vector<Event>::const_iterator event(m_events.begin());
   for ( ; event != m_events.end(); ++event) {
      double sep(event->sep(evt));
      double value(psf(event->eventClass()).value(sep, event->energy(),
                                                  theta, 0));
      wts.insert(std::make_pair(*event, value));
   }
}

void PsfClusters::loadIrfs(const std::string & irfs) {
   irfLoader::Loader::go(irfs);
   const std::vector<std::string> & irfNames =
      irfLoader::Loader::respIds().find(irfs)->second;
   std::cerr << "Using IRFs: " << std::endl;
   for (size_t i(0); i < irfNames.size(); i++) {
      std::cerr << "  " << irfNames.at(i) << std::endl;
      irfInterface::Irfs * irf = 
         irfInterface::IrfsFactory::instance()->create(irfNames.at(i));
      m_psfs[irf->irfID()] = irf->psf()->clone();
      delete irf;
   }
}

const irfInterface::IPsf & PsfClusters::psf(size_t item) const {
   typedef std::map<size_t, irfInterface::IPsf *> PsfMap_t;
   PsfMap_t::const_iterator it(m_psfs.find(item));
   if (it == m_psfs.end()) {
      std::cout << "Available IRF classes: \n";
      for (PsfMap_t::const_iterator foo(m_psfs.begin()); 
           foo != m_psfs.end(); ++foo) {
         std::cout << foo->first << std::endl;
      }
      std::ostringstream message;
      message << "Error accessing IRF for event class " << item;
      throw std::runtime_error(message.str());
   }
   return *(it->second);
}

} // namespace grbASP
