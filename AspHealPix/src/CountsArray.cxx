/**
 * @file CountsArray.cxx
 * @brief  Subclass of HealpixArray for representing binned counts on 
 * the sky.
 *
 * @author J. Chiang <jchiang@slac.stanford.edu>
 *
 * $Header$
 */

#include "tip/IFileSvc.h"
#include "tip/Header.h"
#include "tip/Table.h"

#include "astro/SkyDir.h"

#include "AspHealPix/CountsArray.h"

CountsArray::CountsArray(healpix::Healpix hp) : HealpixArray(hp) {}

CountsArray::CountsArray(const std::string & infile, 
                         const std::string & extname,
                         const std::string & fieldname)
   : HealpixArray(infile, extname, fieldname) {}

CountsArray::CountsArray(const HealpixArray & array) : HealpixArray(array) {}

void CountsArray::write(const std::string & outfile) const {
   HealpixArray::write(outfile, "binned_counts", "counts");
}

CountsArray CountsArray::operator+(const CountsArray & x) const {
   return CountsArray(HealpixArray::operator+(x));
}

CountsArray CountsArray::operator-(const CountsArray & x) const {
   return CountsArray(HealpixArray::operator-(x));
}

void CountsArray::binCounts(const std::string & ft1file, 
                            const std::string & filter) {
   const tip::Table * table 
      = tip::IFileSvc::instance().readTable(ft1file, "EVENTS", filter);
   tip::Table::ConstIterator it(table->begin());
   tip::ConstTableRecord & row(*it);
   for (; it != table->end(); ++it) {
      double ra, dec;
      row["RA"].get(ra);
      row["DEC"].get(dec);
      astro::SkyDir dir(ra, dec);
      this->operator[](dir) += 1;
   }
   delete table;
}
