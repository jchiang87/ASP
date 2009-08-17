/** @file HealpixMap.cxx
    @brief implement HealpixMap
$Header$
*/

#include "healpix/HealpixMap.h"
#include "healpix/HealPixel.h"
#include <fstream>
using namespace healpix;

HealpixMap::HealpixMap(int level)
:  m_level(level)
{}

HealpixMap::~HealpixMap()
{}

void HealpixMap::save(std::string filename)
{
    std::ofstream out(filename.c_str());
    out << m_level << std::endl;
    for( const_iterator it = begin(); it!= end(); ++it){
        out << it->first << "\t" << it->second << std::endl;
    }
}

void HealpixMap::load(std::string filename)
{
    std::ifstream in(filename.c_str());
    in >> m_level;
    while(!in.eof()){
        int index;
        float ts;
        in >> index >> ts;
        (*this)[index] = ts;
    }
}



double HealpixMap::operator ()(const astro::SkyDir& dir)const
{
    HealPixel hp(dir, m_level);
    const_iterator it (find(hp.index()) );
    return it != end() ? it->second : 0;   
}

   
