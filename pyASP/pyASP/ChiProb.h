/**
 * @file ChiProb.cxx
 * @brief Functions to compute delta chi-square probabilities.
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#ifndef pyASP_ChiProb_h
#define pyASP_ChiProb_h

#include <string>

/**
 * class ChiProb
 */

class ChiProb {

public:

   static double ChiProb::gammln(double xx);

   static double ChiProb::gammq(double a, double x);

private:

   static void nrerror(const std::string &);
   static void gcf(double *, double, double, double *);
   static void gser(double *, double, double, double *);

};

#endif // pyASP_ChiProb_h
