/**
 * @file Event.h
 * @brief Encapsulation of LAT photon event.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef grbASP_Event_h
#define grbASP_Event_h

#include "astro/SkyDir.h"

namespace grbASP {

/**
 * @class Event
 */

class Event {

public:

   Event() {}

   Event(double ra, double dec, double time, double energy, int eventClass) 
      : m_dir(astro::SkyDir(ra, dec)), m_time(time), m_energy(energy),
        m_eventClass(eventClass), m_id(s_id++) {}

   double sep(const Event & event) const {
      return m_dir.difference(event.m_dir)*180./M_PI;
   }

   double time() const {
      return m_time;
   }

   double energy() const {
      return m_energy;
   }

   const astro::SkyDir & dir() const {
      return m_dir;
   }

   int eventClass() const {
      return m_eventClass;
   }

   bool operator==(const Event & event) const {
      return m_id == event.m_id;
   }

   bool operator!=(const Event & event) const {
      return m_id != event.m_id;
   }

   bool operator<(const Event & other) const {
      return m_id < other.m_id;
   }

private:

   astro::SkyDir m_dir;
   double m_time;
   double m_energy;
   int m_eventClass;
   unsigned int m_id;

   static unsigned int s_id;

};

} // namespace grbASP

#endif // grbASP_Event_h
