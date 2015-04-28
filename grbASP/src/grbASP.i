// -*- mode: c++ -*-
/**
 * @file grbASP.i
 * @brief Interface file for SWIG generated wrappers.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */
%module grbASP
%{
#include <fenv.h>
#include <stdexcept>
#include <string>
#include <vector>
#include "astro/JulianDate.h"
#include "astro/SkyDir.h"
#include "astro/SkyProj.h"
#include "astro/SolarSystem.h"
astro::JulianDate jd_from_MET(double met) {
   return astro::JulianDate(astro::JulianDate::missionStart() + met/8.64e4);
}
#include "grbASP/Event.h"
#include "grbASP/ClusterAlg.h"
#include "grbASP/EventClusters.h"
#include "grbASP/PsfClusters.h"
#include "grbASP/ScData.h"
#include "grbASP/RootNTupleBase.h"
%}
%include stl.i
%exception {
   try {
      $action
   } catch (std::exception & eObj) {
      PyErr_SetString(PyExc_RuntimeError, const_cast<char*>(eObj.what()));
      return NULL;
   }
}
%template(DoublePair) std::pair<double, double>;
%template(DoubleVector) std::vector<double>;
%template(PairVector) std::vector< std::pair<double, double> >;
%template(StringVector) std::vector<std::string>;
%template(ClusterAlgResults) std::pair<std::pair<double, double>, astro::SkyDir>;
%feature("autodoc", "1");
%include astro/JulianDate.h
%include astro/SkyProj.h
%include astro/SkyDir.h
%include astro/SolarSystem.h
astro::JulianDate jd_from_MET(double met);
%include grbASP/ScData.h
%include grbASP/Event.h
%template(EventVector) std::vector<grbASP::Event>;
%include grbASP/ClusterAlg.h
%include grbASP/EventClusters.h
%include grbASP/PsfClusters.h
%include grbASP/RootNTupleBase.h
%extend grbASP::Event {
   static void enableFPE() {
      feenableexcept(FE_INVALID | FE_DIVBYZERO | FE_OVERFLOW);
   }
}
%extend astro::SkyDir {
   static astro::SkyDir interpolate(const astro::SkyDir & dir1, 
                                    const astro::SkyDir & dir2,
                                    double t1, double t2, double tt) {
      return astro::SkyDir((tt - t1)/(t2 - t1)*(dir2() - dir1()) + dir1());
   }
   astro::SkyDir operator+(const astro::SkyDir & other) {
      return astro::SkyDir(self->operator()() + other());
   }
}
%extend astro::JulianDate {
   std::vector<double> gregorianDate() {
      int year, month, day;
      double hours;
      self->getGregorianDate(year, month, day, hours);
      std::vector<double> data;
      data.push_back(year);
      data.push_back(month);
      data.push_back(day);
      data.push_back(hours);
      return data;
   }
}
%extend grbASP::ClusterAlg {
   std::pair< std::pair<double, double>, astro::SkyDir>
      processEvents(const std::vector<Event> & events, double bg_rate=0,
                    double radius=10) {
      double logLike_time, logLike_pos;
      astro::SkyDir meanDir;
      self->process(events, logLike_time, logLike_pos, meanDir, 
                    bg_rate, radius);
      return std::make_pair(std::make_pair(logLike_time,logLike_pos), meanDir);
   }
}
%extend astro::SolarSystem {
   static astro::SkyDir sunDirection(double met) {
      astro::JulianDate jd(astro::JulianDate::missionStart() + met/8.64e4);
      astro::SolarSystem sun;
      return sun.direction(jd);
   }
}
%extend grbASP::RootNTupleBase {
   const std::vector<double> & __getitem__(const std::string & name) const {
      return self->operator[](name);
   }
}
