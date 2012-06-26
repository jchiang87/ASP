/**
 * @file PoissonProb.h
 * @brief Static functions that return HealpixArrays of Poisson
 * probabilities of observed counts given HealpixArrys of model counts
 * and exposure.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef _AspHealPix_PoissonProb_h
#define _AspHealPix_PoissonProb_h

class CountsArray;
class ExposureArray;
class HealpixArray;

/**
 * @class PoissonProb
 */

class PoissonProb {

public:

  static HealpixArray compute(const HealpixArray & intensity,
                              const CountsArray & counts,
                              const ExposureArray & exposure);

  static HealpixArray compute(const CountsArray & counts0,
                              const ExposureArray & exposure0,
                              const CountsArray & counts1,
                              const ExposureArray & exposure1);

};

#endif // _AspHealPix_PoissonProb_h

