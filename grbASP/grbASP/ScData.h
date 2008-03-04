/**
 * @file ScData.h
 * @brief Encapsulation of Spacecraft data
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef grbASP_ScData_h
#define grbASP_ScData_h

#include <string>

#include "astro/SkyDir.h"

namespace grbASP {

class ScData {

public:
   
   ScData(const std::string & ft2File);

   astro::SkyDir zaxis(double time) const;

   double inclination(double time, const astro::SkyDir & srcDir) const;

};

} // namespace grbASP

#endif // grbASP_ScData_h
