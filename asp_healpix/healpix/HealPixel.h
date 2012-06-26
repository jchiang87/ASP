/** @file HealPixel.h
@brief Define the HealPixel class 
$Header$
*/

#ifndef healpix_HealPixel_h
#define healpix_HealPixel_h

#include "astro/SkyDir.h"
#include <vector>

namespace healpix {
/**@class HealPixel
    @brief represent a Healpix pixel, assuming nested indexing

    This allows for a mixture of different nest levels (note that nside is forced to 
    be a power of 2) with a class variable to describe the coordinate system to use

    The sorting, defined by the operator<, follows the pixel indexing, with outer pixels preceding.
    A "band" indentifier, if present, will be used to refine the sort order, the most rapid.

    @author T. Burnett <tburnett@u.washington.edu>
    */
    class HealPixel{
    public:
        ///@brief construct a pixel from the index and level (nside = 2**level).
        HealPixel(unsigned long index=0, unsigned int level=5);

        ///@brief construct a pixel from the index and level (nside = 2**level).
        HealPixel(unsigned long index, unsigned int level, unsigned int band);

        ///@brief create a HealPixel from a direction, and a level (nside=2**level)
        HealPixel(const astro::SkyDir& dir, unsigned int level);

        ///@brief create a HealPixel from a direction, and a level 
        ///@param level must be in range 0-13; nside=2**level
        ///@param band  energy band, which must be 0-255
        HealPixel(const astro::SkyDir& dir, unsigned int level, unsigned int band);

        ///@brief behave like a skydir object, in center of pixel
        operator astro::SkyDir()const;
        astro::SkyDir operator()()const{ return *this;}

        long index()const{return m_index;} ///< the pixel index

        unsigned int level()const{return m_data>>8;} ///< the level, where nside=2**level
        unsigned int band()const {return m_data & 255;} ///< the band id
        
        int nside()const{return  1<<level();} ///< the Healpix parameter nside

        double area()const{return (4 * M_PI)/(12 * nside() * nside());}///< solid angle
        
        long lastChildIndex(int childLevel)const; // largest index for my child at given level.

        /// sort operator
        bool operator<(const HealPixel& other)const;
        
        /// other comparison operators
        bool operator==(const HealPixel& other)const;
        bool operator!=(const HealPixel& other)const;
        bool operator<=(const HealPixel& other)const;

        static bool test(); // should be true


        /// @brief return a list of neighbors, all with same level/band
        std::vector<HealPixel> neighbors() const;

        /// set the coordinate system for all pixels
        static void setCoordinateSystem(astro::SkyDir::CoordSystem sys);

    private:

        void setup(const astro::SkyDir& dir);
        unsigned int data()const{return m_data;}

        /// use the same coordinate system for all these objects
       static astro::SkyDir::CoordSystem s_coordsys;

        long m_index; ///< the Healpix nested index
        unsigned int m_data;   ///< packed level and energy band
#if 0
        int m_level;  ///< nesting level: nside is 2**level, combinded with band index
#endif
    };

}
#endif

