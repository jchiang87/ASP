/**
 * @file ScData.cxx
 * @brief Encapsulation of Spacecraft data
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <cmath>

#include "astro/GPS.h"

#include "grbASP/ScData.h"

namespace grbASP {

ScData::ScData(const std::string & ft2File) {
   astro::GPS::instance()->setPointingHistoryFile(ft2File);
}

astro::SkyDir ScData::zaxis(double time) const {
   return astro::GPS::instance()->zAxisDir(time);
}

double ScData::inclination(double time, const astro::SkyDir & srcDir) const {
   return astro::GPS::instance()->zAxisDir(time).difference(srcDir)*180./M_PI;
}

} // namespace grbASP
