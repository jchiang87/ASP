// -*- mode: c++ -*-
%module BayesianBlocks
%{
#include <fenv.h>
#include <utility>
#include <vector>
#include "BayesianBlocks/BayesianBlocks.h"
#include "BayesianBlocks/BayesianBlocks2.h"
#include "BayesianBlocks/Exposure.h"
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
%template(DoubleVector) std::vector<double>;
%template(PairDoubleVector) std::pair<std::vector<double>,std::vector<double> >;
%template(DoubleVectorVector) std::vector< std::vector<double> >;
%template(IntVector) std::vector<int>;
%include BayesianBlocks/BayesianBlocks.h
%include BayesianBlocks/BayesianBlocks2.h
%include BayesianBlocks/Exposure.h
%extend BayesianBlocks2 {
   std::pair<std::vector<double>, std::vector<double> > 
      lightCurve(double ncp_prior) {
      std::vector<double> xx, yy;
      self->globalOpt(ncp_prior, xx, yy);
      return std::make_pair(xx, yy);
   }
}
%extend BayesianBlocks {
   static void enableFPE() {
      feenableexcept(FE_INVALID | FE_DIVBYZERO | FE_OVERFLOW);
   }
   std::vector< std::vector<double> > lightCurve(double ncpPrior) {
      std::vector<double> tmins;
      std::vector<double> tmaxs;
      std::vector<double> numEvents;
      std::vector<double> exposures;
      self->computeLightCurve(ncpPrior, tmins, tmaxs, numEvents, exposures);

      std::vector<double> xx;
      std::vector<double> yy;
      for (size_t i(0); i < tmins.size(); i++) {
         xx.push_back(tmins.at(i));
         xx.push_back(tmaxs.at(i));
         yy.push_back(numEvents.at(i)/exposures.at(i));
         yy.push_back(numEvents.at(i)/exposures.at(i));
      }

      std::vector< std::vector<double> > output;
      output.push_back(xx);
      output.push_back(yy);
      return output;
   }
}
