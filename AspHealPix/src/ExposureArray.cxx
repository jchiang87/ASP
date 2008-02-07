/**
 * @file ExposureArray.cxx
 * @brief Subclass of HealpixArray for representing instrument exposure
 * corresponding to a CountsArray.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <cmath>

#include <sstream>
#include <stdexcept>

#include "st_facilities/Util.h"

#include "irfInterface/Irfs.h"
#include "irfInterface/IrfsFactory.h"

#include "irfLoader/Loader.h"

#include "map_tools/Exposure.h"

#include "AspHealPix/ExposureArray.h"

namespace {
   class PowerLaw {
   public:
      PowerLaw(double index, double norm=1) : m_index(index), m_norm(norm) {}
      double operator()(double energy) const {
         return m_norm*std::pow(energy, m_index);
      }
      double integral(double emin, double emax) const {
         if (m_index == -1) {
            return m_norm*std::log(emax/emin);
         }
         return m_norm/(m_index + 1)*(std::pow(emax, m_index+1) -
                                      std::pow(emin, m_index+1));
      }
   private:
      double m_index;
      double m_norm;
   };

   double pl_integral(double x1, double x2, double y1, double y2) {
      double indx(std::log(y2/y1)/std::log(x2/x1));
      double prefactor(y1/std::pow(x1, indx));
      if (indx == -1) {
         return prefactor*std::log(x2/x1);
      }
      return prefactor/(indx+1)*(std::pow(x2, indx+1) - std::pow(x1, indx+1));
   }
} // anonymous namespace

ExposureArray::ExposureArray(healpix::Healpix hp) : HealpixArray(hp) {}

ExposureArray::ExposureArray(const std::string & infile, 
                             const std::string & extname,
                             const std::string & fieldname)
   : HealpixArray(infile, extname, fieldname) {}

ExposureArray::ExposureArray(const HealpixArray & array) 
   : HealpixArray(array) {}

void ExposureArray::write(const std::string & outfile) const {
   HealpixArray::write(outfile, "Exposure", "Exposure");
}

ExposureArray ExposureArray::operator+(const ExposureArray & x) const {
   return ExposureArray(HealpixArray::operator+(x));
}

ExposureArray ExposureArray::operator-(const ExposureArray & x) const {
   return ExposureArray(HealpixArray::operator-(x));
}

void ExposureArray::computeExposure(const std::string & irfs,
                                    const std::string & livetimeCube,
                                    double photonIndex,
                                    double emin, double emax,
                                    size_t nenergies) {
   IrfsMap_t irfsMap(getIrfs(irfs));
   if (!st_facilities::Util::fileExists(livetimeCube)) {
      throw std::runtime_error("File " + livetimeCube + " not found.");
   }
   map_tools::Exposure livetime(livetimeCube);

   PowerLaw pl(-photonIndex);
   double integral(pl.integral(emin, emax));

   std::vector<Aeff> aeffs;
   std::vector<double> pl_vals;

   double estep(std::log(emax/emin)/(nenergies-1));
   std::vector<double> energies;
   for (size_t k(0); k < nenergies; k++) {
      energies.push_back(emin*std::exp(estep*k));
      aeffs.push_back(Aeff(irfsMap, energies.back()));
      pl_vals.push_back(pl(energies.back()));
   }

   for (ExposureArray::iterator it(begin()); it != end(); ++it) {
      std::vector<double> integrand;
      for (size_t k(0); k < energies.size(); k++) {
         integrand.push_back(livetime(dir(it), aeffs.at(k))*pl_vals.at(k));
      }
      *it = 0;
      for (size_t k(0); k < energies.size()-1; k++) {
         *it += pl_integral(energies.at(k), energies.at(k+1),
                            integrand.at(k), integrand.at(k+1));
      }
      *it /= integral;
   }
}

std::map<int, irfInterface::Irfs *> 
ExposureArray::getIrfs(const std::string & irfs) {
   irfLoader::Loader_go();
   irfInterface::IrfsFactory *myFactory(irfInterface::IrfsFactory::instance());
   
   typedef std::map< std::string, std::vector<std::string> > RespIdMap_t;

   const RespIdMap_t & responseIds = irfLoader::Loader_respIds();
   RespIdMap_t::const_iterator it(responseIds.find(irfs));

   if (it == responseIds.end()) {
      std::ostringstream message;
      message << "Invalid response function choice: " << irfs << "\n"
              << "Valid choices are \n";
      for (RespIdMap_t::const_iterator resp = responseIds.begin();
           resp != responseIds.end(); ++resp) {
         message << resp->first << "\n";
      }
      throw std::invalid_argument(message.str());
   }
   
   const std::vector<std::string> & resps = it->second;
   IrfsMap_t my_irfMap;
   for (size_t i = 0; i < resps.size(); i++) {
      irfInterface::Irfs * my_irfs(myFactory->create(resps.at(i)));
      my_irfMap[my_irfs->irfID()] = my_irfs;
   }
   return my_irfMap;
}

ExposureArray::Aeff::Aeff() : m_irfsMap(0) {}

ExposureArray::Aeff::Aeff(const IrfsMap_t & irfsMap, double energy)
   : m_irfsMap(&irfsMap), m_energy(energy) {}

double ExposureArray::Aeff::operator()(double costheta) const {
   double phi(0);
   double inc(std::acos(costheta)*180./M_PI);
   IrfsMap_t::const_iterator irfs(m_irfsMap->begin());
   double value(0);
   for (; irfs != m_irfsMap->end(); ++irfs) {
      irfInterface::IAeff * aeff(irfs->second->aeff());
      value += aeff->value(m_energy, inc, phi);
   }
   return value;
}
