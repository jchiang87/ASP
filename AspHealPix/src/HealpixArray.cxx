/**
 * @file HeapixArray.cxx
 * @brief Implementation for subclass of healpix::HealpixArray<float> with
 * FITS I/O member functions.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include <stdexcept>

#include "tip/IFileSvc.h"
#include "tip/Header.h"
#include "tip/Table.h"

#include "astro/SkyDir.h"

#include "healpix/HealpixArrayIO.h"

#include "map_tools/SkyImage.h"

#include "AspHealPix/HealpixArray.h"

HealpixArray::HealpixArray() : healpix::HealpixArray<float>(healpix::Healpix()) {
   fillCoordArrays();
}

HealpixArray::HealpixArray(healpix::Healpix hp) 
   : healpix::HealpixArray<float>(hp) {
   fillCoordArrays();
}

HealpixArray::HealpixArray(const std::string & infile, 
                           const std::string & extname,
                           const std::string & fieldname) {
   const healpix::HealpixArray<float> & my_array = 
      healpix::HealpixArrayIO::instance().read(infile,extname,fieldname);
   
   healpix::Healpix my_hp(my_array.healpix().nside(), 
                        my_array.healpix().ord(),
                        coordsys(infile, extname));
   *this = HealpixArray(my_hp);
   for (size_t i(0); i < my_array.size(); i++) {
      at(i) = my_array.at(i);
   }
   fillCoordArrays();
}

HealpixArray::~HealpixArray() {}

void HealpixArray::write(const std::string & outfile, 
                         const std::string & extname,
                         const std::string & fieldname) const {
   std::auto_ptr<tip::Table> table = 
      healpix::HealpixArrayIO::instance().write(*this, outfile, extname,
                                                  fieldname, true);
   tip::Header & header(table->getHeader());
   header["COORDSYS"].set(static_cast<int>(healpix().coordsys()));
}

void HealpixArray::writeImage(const std::string & outfile,
                              double pixel_size, bool galactic) const {
   astro::SkyDir::CoordSystem coordsys(astro::SkyDir::EQUATORIAL);
   if (galactic) {
      coordsys = astro::SkyDir::GALACTIC;
   }
   double fov;
   int layers;
   std::string proj;
   map_tools::SkyImage image(astro::SkyDir(0, 0, coordsys), outfile,
                             pixel_size, fov=360, layers=1, proj="AIT",
                             galactic);
   image.fill(*this);
}

HealpixArray HealpixArray::inverse(){
  HealpixArray y(healpix());                                           
  for (size_t i(0); i < size(); i++) {
    if(at(i)!=0.){
      y.at(i) = 1./at(i);
    } else {
      std::cout<<"HealpixArray::inverse encountered a divide by 0 at pixel "<<i<<std::endl;
    }
  }
  return y;
}

void 
HealpixArray::subSelect(
                        const std::string& infile, 
                        const std::string& outfile, long idx, 
                        const std::string & extname)
{
  //first create the new file and
  //get a pointer to the table for writing
  tip::IFileSvc::instance().createFile(outfile, infile);
  tip::Table * outTable 
    = tip::IFileSvc::instance().editTable(outfile, extname);
  
  //read input file and resize output table
  const tip::Table * inTable 
    = tip::IFileSvc::instance().readTable(infile, extname);
  outTable->setNumRecords(inTable->getNumRecords());
  
  //loop over input table and make selection
  tip::Table::Iterator outIt = outTable->begin();
  tip::Table::Record & out = *outIt;
  long npts(0);
  for(tip::Table::ConstIterator it = inTable->begin();
      it!=inTable->end(); it++)
    {
      tip::ConstTableRecord & in = *it;
      double l = in["L"].get();
      double b = in["B"].get();
      astro::SkyDir::CoordSystem 
        coordsys=astro::SkyDir::EQUATORIAL;
      astro::SkyDir recordDir(l, b, coordsys);
      healpix::Healpix::Pixel pix(recordDir, healpix());
      if(pix.index()==idx){
        out = in;
        ++outIt;
        npts++;
      }
    }
  outTable->setNumRecords(npts);
  outTable->getHeader().addHistory("Subselected by pixel direction");

  delete inTable;
  delete outTable;
}

#undef _DEFINE_BINARY_OPERATOR
#define _DEFINE_BINARY_OPERATOR(_Op, _Name)                             \
HealpixArray HealpixArray::operator _Op(const HealpixArray & x) const { \
   HealpixArray y(healpix());                                           \
   for (size_t i(0); i < size(); i++) {                                 \
      y.at(i) = at(i) _Op x.at(i);                                      \
   }                                                                    \
   return y;                                                            \
}

_DEFINE_BINARY_OPERATOR(+, plus)
_DEFINE_BINARY_OPERATOR(-, minus)
_DEFINE_BINARY_OPERATOR(*, times)
_DEFINE_BINARY_OPERATOR(/, divide)
#undef _DEFINE_BINARY_OPERATOR

#define _DEFINE_BINARY_OPERATOR(_Op, _Name)                             \
HealpixArray HealpixArray::operator _Op(double x) const {               \
   HealpixArray y(healpix());                                           \
   for (size_t i(0); i < size(); i++) {                                 \
      y.at(i) = at(i) _Op x;                                            \
   }                                                                    \
   return y;                                                            \
}

_DEFINE_BINARY_OPERATOR(+, plus)
_DEFINE_BINARY_OPERATOR(-, minus)
_DEFINE_BINARY_OPERATOR(*, times)
_DEFINE_BINARY_OPERATOR(/, divide)
#undef _DEFINE_BINARY_OPERATOR

HealpixArray HealpixArray::operator-() const {
   HealpixArray y(healpix());
   for (size_t i(0); i < size(); i++) {
      y.at(i) = -at(i);
   }
   return y;
}

double HealpixArray::operator()(const astro::SkyDir & dir) const {
   return operator[](dir);
}

healpix::Healpix HealpixArray::healpix() const {
   return healpix::HealpixArray<float>::healpix();
}

const std::vector<float> & HealpixArray::values() const {
   return *this;
}

const std::vector<float> & HealpixArray::glon() const {
   return m_glon;
}

const std::vector<float> & HealpixArray::glat() const {
   return m_glat;
}

void HealpixArray::writeLayeredImage(const std::vector<HealpixArray> & arrays,
                                     const std::string & outfile,
                                     double pixel_size, bool galactic) {
   astro::SkyDir::CoordSystem coordsys(astro::SkyDir::EQUATORIAL);
   if (galactic) {
      coordsys = astro::SkyDir::GALACTIC;
   }
   double fov;
   int layers;
   std::string proj;
   map_tools::SkyImage image(astro::SkyDir(0, 0, coordsys), outfile,
                             pixel_size, fov=360, layers=arrays.size(), 
                             proj="AIT", galactic);
   for (size_t i(0); i < arrays.size(); i++) {
      image.fill(arrays.at(i), i);
   }
}

void HealpixArray::fillCoordArrays() {
   healpix::Healpix hp = healpix();
   m_glon.clear();
   m_glat.clear();
   healpix::Healpix::const_iterator pixel(hp.begin());
   for (; pixel != hp.end(); ++pixel) {
      double glon((*pixel)().l());
      if (glon > 180) {
         glon -= 360;
      }
      m_glon.push_back(glon);
      m_glat.push_back((*pixel)().b());
   }
}

astro::SkyDir::CoordSystem 
HealpixArray::coordsys(const std::string & infile,
                       const std::string & extname) const {
   const tip::Table * table(tip::IFileSvc::instance().readTable(infile,
                                                                extname));
   const tip::Header & header(table->getHeader());
   int coordsys_int;
   header["COORDSYS"].get(coordsys_int);
   astro::SkyDir::CoordSystem coordsys(astro::SkyDir::EQUATORIAL);
   if (coordsys_int == 0) {
      coordsys = astro::SkyDir::GALACTIC;
   }
   delete table;
   return coordsys;
}
