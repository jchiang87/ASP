/** @file HealpixArrayIO.cxx
@brief Define the CosineBinner classixel 

@author T. Burnett

$Header$
*/

#include "healpix/HealpixArrayIO.h"
#include "tip/IFileSvc.h"

#include <cmath>
#include <errno.h>
#include <sstream>
#include <string>
#include <typeinfo>
#include <stdexcept>
#include <cassert>

using namespace healpix;

namespace {

    // set header fields for the array.
    template<class T>
    void setHealpixHeaderFields( const HealpixArray<T> & ha, int columns, tip::Header& hdr)
    {
        const Healpix& hp = ha.healpix();
        hdr["ORDERING"].set(hp.ord() == Healpix::NEST? "NESTED": "RING"); 
        hdr["COORDSYS"].set(hp.galactic()? "GAL" : "EQU");
        hdr["NSIDE"].set(hp.nside()); 
        hdr["FIRSTPIX"].set(0); 
        hdr["LASTPIX"].set(ha.size()-1); 
        hdr["NAXIS1"].set( columns* sizeof(float) );
    }
    std::string coordsystem(const tip::Header& hdr){
        std::string value;
        try{ // new value
            hdr["COORDSYS"].get(value);
        }catch(const std::exception &){
            // allow old value
            hdr["COORDTYPE"].get(value);
        }
        return value;
    }


}// anon namespace

// Get the instance of the singleton class.
HealpixArrayIO & HealpixArrayIO::instance()
{
    static bool first_time = true;

    // Perform any initialization only once
    if (first_time)
    {
        first_time = false;
    }

    // Create the singleton class.
    static HealpixArrayIO s_HealpixArrayIO;

    return s_HealpixArrayIO;
}

std::auto_ptr<tip::Table> HealpixArrayIO::write(const HealpixArray<CosineBinner> & ha,
                                                const std::string & outputFile,
                                                const std::string & tablename, bool clobber)
{
    if (clobber)
    {
        int rc = std::remove(outputFile.c_str());
        if( rc == -1 && errno == EACCES ) 
            throw std::runtime_error(std::string(" Cannot remove file " + outputFile));
    }

    // now add a table to the file
    tip::IFileSvc::instance().appendTable(outputFile, tablename);
    tip::Table & table = *tip::IFileSvc::instance().editTable( outputFile, tablename);

    // this is a work-around for a bug in tip v2r1p1

    std::stringstream ss;
    size_t size = ha[0].size(); // get individual size from first one
    ss << size << "E";
    std::string nbrbins = ss.str();
    table.appendField("COSBINS", ss.str());
    tip::Index_t numrecs =  ha.size() ;
    table.setNumRecords(numrecs);

    // get iterators for the Table and the HealpixArray
    tip::Table::Iterator itor = table.begin();
    HealpixArray<healpix::CosineBinner>::const_iterator haitor = ha.begin();

    // now just copy
    for( ; haitor != ha.end(); ++haitor, ++itor)
    {
        assert( (*haitor).size() == size); // all must have same size
        (*itor)["COSBINS"].set(*haitor);
    }

    // set the headers (TODO: do the comments, too)
    tip::Header& hdr = table.getHeader();
    setHealpixHeaderFields(ha, size, hdr);

    hdr["THETABIN"].set(CosineBinner::thetaBinning());
    hdr["NBRBINS"].set(CosineBinner::nbins());
    hdr["COSMIN"].set(CosineBinner::cosmin());
    hdr["PHIBINS"].set(CosineBinner::nphibins());

    // need to do this to ensure file is closed when pointer goes out of scope
    return std::auto_ptr<tip::Table>(&table); 
}

std::auto_ptr<tip::Table> HealpixArrayIO::write(const HealpixArray<float> & ha,
                                                const std::string & outputFile,
                                                const std::string & tablename,
                                                const std::string & fieldname,
                                                bool clobber)
{
    if (clobber)
    {
        int rc = std::remove(outputFile.c_str());
        if( rc == -1 && errno == EACCES ) 
            throw std::runtime_error(std::string(" Cannot remove file " + outputFile));
    }

    // now add a table to the file
    tip::IFileSvc::instance().appendTable(outputFile, tablename);
    tip::Table & table = *tip::IFileSvc::instance().editTable( outputFile, tablename);

    // this is a work-around for a bug in tip v2r1p1

    table.appendField(fieldname, "1E");
    table.setNumRecords(ha.size());

    // get iterators for the Table and the HealpixArray
    tip::Table::Iterator itor = table.begin();
    HealpixArray<float>::const_iterator haitor = ha.begin();

    // now just copy
    for( ; haitor != ha.end(); ++haitor, ++itor)
    {
        (*itor)[fieldname].set(*haitor);
    }

    // set the headers (TODO: do the comments, too)
    tip::Header& hdr = table.getHeader();
#if 0 // is this really 1 column?
    hdr["NAXIS1"].set(sizeof(float));
#endif
    setHealpixHeaderFields(ha, 1, hdr);

    // need to do this to ensure file is closed when pointer goes out of scope
    return std::auto_ptr<tip::Table>(&table); 
}


std::auto_ptr<tip::Table> HealpixArrayIO::write(const HealpixArray<std::vector<float> > & ha,
                                                const std::string & outputFile,
                                                const std::string & tablename,
                                                const std::vector<std::string> & fieldname,
                                                bool clobber)
{
    if (clobber)
    {
        int rc = std::remove(outputFile.c_str());
        if( rc == -1 && errno == EACCES ) 
            throw std::runtime_error(std::string(" Cannot remove file " + outputFile));
    }

    // now add a table to the file
    tip::IFileSvc::instance().appendTable(outputFile, tablename);
    tip::Table & table = *tip::IFileSvc::instance().editTable( outputFile, tablename);

    // this is a work-around for a bug in tip v2r1p1

    // Add all field names
    for (std::vector<std::string>::const_iterator sit = fieldname.begin();
        sit != fieldname.end(); ++ sit)
    {
        table.appendField(*sit, "1E");
    }
    table.setNumRecords(ha.size());

    // get iterators for the Table and the HealpixArray
    tip::Table::Iterator itor = table.begin();
    HealpixArray<std::vector<float> >::const_iterator haitor = ha.begin();

    // now just copy
    for( ; haitor != ha.end(); ++haitor, ++itor)
    {

        std::vector<float>::const_iterator flit = (*haitor).begin();
        for (std::vector<std::string>::const_iterator sit = fieldname.begin();
            sit != fieldname.end(); ++ sit, ++flit)
        {
            if (flit == (*haitor).end())
                throw std::runtime_error(std::string("Number of field names provided excedes number of data elements per pixel."));
            (*itor)[*sit].set(*flit);
        }
    }

    // set the headers (TODO: do the comments, too)
    tip::Header& hdr = table.getHeader();

    setHealpixHeaderFields(ha, fieldname.size(), hdr);

    // need to do this to ensure file is closed when pointer goes out of scope
    return std::auto_ptr<tip::Table>(&table); 
}



HealpixArray<CosineBinner> HealpixArrayIO::read(const std::string & inputFile,
                                                const std::string & tablename)
{
    /* If the caller passes a reference to a HealpixArray instead of having this routine
    return a HealpixArray, how does the caller know what to set for nside, s_nbins, etc.?
    Could provide a GetAddtibutes function for this purpose.  If a reference is
    passed, this routine should throw an exception if the attributes of the
    HealpixArray passed don't match those of the file being read.  */

    const tip::Table & table=*tip::IFileSvc::instance().readTable(inputFile, tablename);
    const tip::Header& hdr = table.getHeader();
    int nside=0;
    hdr["NSIDE"].get(nside);
    std::string ordering;
    hdr["ORDERING"].get(ordering);
    Healpix::Ordering ord = (ordering == "NESTED")?
        Healpix::NEST: Healpix::RING;
    std::string thetabinstring;
    hdr["THETABIN"].get(thetabinstring);
    bool thetabin = (thetabinstring == "COSTHETA")? false: true;
    int nbrbins;
    hdr["NBRBINS"].get(nbrbins);
    double cosmin;
    hdr["COSMIN"].get(cosmin);


    int nphibins(0);
    try{
        hdr["PHIBINS"].get(nphibins);
    }catch(...){}

    // Code for setting CoordSystem added 1/17/2008
    std::string check(coordsystem(hdr));

    astro::SkyDir::CoordSystem coordsys = (check == "GAL")?
        astro::SkyDir::GALACTIC: astro::SkyDir::EQUATORIAL;

    CosineBinner::setBinning(cosmin, nbrbins, thetabin);
    if( nphibins>0){
        CosineBinner::setPhiBins(nphibins);
    }
    HealpixArray<healpix::CosineBinner> ha(Healpix(nside, ord, coordsys));

    tip::Table::ConstIterator itor = table.begin();
    HealpixArray<CosineBinner>::iterator haitor = ha.begin();

    for( ; itor != table.end(); ++haitor, ++itor)
    {
        (*itor)["COSBINS"].get(*haitor);
    }
    delete &table; 
    return ha;
}

HealpixArray<float> HealpixArrayIO::read(const std::string & inputFile,
                                         const std::string & tablename,
                                         const std::string & fieldname)
{
    /* If the caller passes a reference to a HealpixArray instead of having this routine
    return a HealpixArray, how does the caller know what to set for nside, s_nbins, etc.?
    Could provide a GetAddtibutes function for this purpose.  If a reference is
    passed, this routine should throw an exception if the attributes of the
    HealpixArray passed don't match those of the file being read.  */

    const tip::Table & table=*tip::IFileSvc::instance().readTable(inputFile, tablename);
    const tip::Header& hdr = table.getHeader();
    int nside=0;
    hdr["NSIDE"].get(nside);
    std::string ordering;
    hdr["ORDERING"].get(ordering);
    Healpix::Ordering ord = (ordering == "NESTED")?
        Healpix::NEST: Healpix::RING;

    // Code for setting CoordSystem added 1/17/2008
    std::string check( coordsystem(hdr));
    astro::SkyDir::CoordSystem coordsys = (check == "GAL")?
        astro::SkyDir::GALACTIC: astro::SkyDir::EQUATORIAL;

    HealpixArray<float> ha(Healpix(nside, ord, coordsys));

    tip::Table::ConstIterator itor = table.begin();
    HealpixArray<float>::iterator haitor = ha.begin();

    for( ; itor != table.end(); ++haitor, ++itor)
    {
        (*itor)[fieldname].get(*haitor);
    }
    delete &table; 
    return ha;
}

HealpixArray<std::vector<float> > HealpixArrayIO::read(const std::string & inputFile,
                                                       const std::string & tablename,
                                                       const std::vector<std::string> & fieldname)
{      
    const tip::Table & table=*tip::IFileSvc::instance().readTable(inputFile, tablename);
    const tip::Header& hdr = table.getHeader();
    int nside=0;
    hdr["NSIDE"].get(nside);
    std::string ordering;
    hdr["ORDERING"].get(ordering);
    Healpix::Ordering ord = (ordering == "NESTED")?
        Healpix::NEST: Healpix::RING;

    // Code for setting CoordSystem added 1/17/2008
    std::string check( coordsystem(hdr));
    astro::SkyDir::CoordSystem coordsys = (check == "GAL")?
        astro::SkyDir::GALACTIC: astro::SkyDir::EQUATORIAL;

    HealpixArray<std::vector<float> > ha(Healpix(nside, ord, coordsys));

    tip::Table::ConstIterator itor = table.begin();
    HealpixArray<std::vector<float> >::iterator haitor = ha.begin();

    for( ; itor != table.end(); ++haitor, ++itor)
    {
        (*haitor).clear();
        for (std::vector<std::string>::const_iterator sit = fieldname.begin();
            sit != fieldname.end(); ++sit)
        {
            float work;
            (*itor)[*sit].get(work);
            (*haitor).push_back(work);
        }
    }
    delete &table; 
    return ha;
}

