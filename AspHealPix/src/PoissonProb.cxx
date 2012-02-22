/**
 * @file PoissonProb.cxx
 * @brief Static functions that return HealpixArrays of Poisson
 * probabilities of observed counts given HealpixArrys of model counts
 * and exposure.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <cmath>

#include "pyASP/ChiProb.h"

#include "AspHealPix/CountsArray.h"
#include "AspHealPix/ExposureArray.h"
#include "AspHealPix/HealpixArray.h"
#include "AspHealPix/PoissonProb.h"

namespace {
   double log10PoissonProb(double counts, double model) {
      static double _log10(std::log(10.));
      if (model == 0 && counts == 0) {
         return 0;
      }
      double value(counts*std::log(model) - model - ChiProb::gammln(counts+1));
      return value/_log10;
   }
} // anonymous namespace

HealpixArray PoissonProb::compute(const HealpixArray & intensity,
                                  const CountsArray & counts,
                                  const ExposureArray & exposure) {
   HealpixArray prob(intensity.healpix());
   for (size_t i(0); i < prob.size(); i++) {
      double model(intensity.at(i)*exposure.at(i));
      prob.at(i) = ::log10PoissonProb(counts.at(i), model);
   }
   return prob;
}

HealpixArray PoissonProb::compute(const CountsArray & counts0,
                                  const ExposureArray & exposure0,
                                  const CountsArray & counts1,
                                  const ExposureArray & exposure1) {
   HealpixArray intens = (counts0 + counts1)/(exposure0 + exposure1);
   HealpixArray prob0 = compute(intens, counts0, exposure0);
   HealpixArray prob1 = compute(intens, counts1, exposure1);
   for (size_t i(0); i < prob0.size(); i++) {
      prob0.at(i) = std::min(prob0.at(i), prob1.at(i));
   }
   return prob0;
}
