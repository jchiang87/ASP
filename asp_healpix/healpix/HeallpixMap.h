/** @file HealpixMap.h
@brief Define the HealpixMap class, and nested classes HealpixMap::Iterator and HealpixMap::Pixel 

@author T. Burnett <tburnett@u.washington.edu>

$Header$
*/

#ifndef healpix_HealpixMap_h
#define healpix_HealpixMap_h

#include "astro/SkyDir.h"
#include "astro/SkyFunction.h"

#include <map>

namespace healpix{

    class HealpixMap :public astro::SkyFunction , std::map<int, float> {
    public:
        HealpixMap(int level = 8);
        ~HealpixMap(){}

        //! @brief  coordinates of a point in the sky
        //! @return value at that point
        virtual double operator()(const astro::SkyDir& dir);

        void save(std::string filename);

        void load(std::string filename);

        float HealpixMap::operator[] (int index)const

    private:
        int m_level;
    };

}

#endif
