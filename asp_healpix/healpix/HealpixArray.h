/** @file HealpixArray.h
@brief Define the HealpixArray template class

@author T. Burnett

$Header$
*/

#ifndef healpix_HealpixArray_h
#define healpix_HealpixArray_h

#include "healpix/Healpix.h"

#include <vector>

namespace healpix {
/** @class HealpixArray<class C>
    @brief Associate a vector of type C with the the Healpix 
    sky tesselization scheme

    It extends a std::vector of the given type, overriding the 
    operator[] with a SkyDir.
*/

template< typename C>
class HealpixArray : public std::vector<C> {
public:

    //! ctor: must pass in a Healpix object to define the binning
    HealpixArray(Healpix hp)
        :m_hp(hp)
    { 
        resize(hp.size());
    }

    //! default ctor, need to set the healpix
    HealpixArray():m_hp(1){resize(m_hp.size());}

    //! return the direction associated with an iterator
    astro::SkyDir dir(typename std::vector<C>::const_iterator it)const{
        healpix::Healpix::Pixel px(it-this->begin(), m_hp);
        return px();
    }

    //! return the dot product of the direction with respect fixed direction
    double dot(typename std::vector<C>::const_iterator it, const astro::SkyDir& extdir)const{
        healpix::Healpix::Pixel px(it-this->begin(), m_hp);
        return px().dir().dot(extdir());
    }


    //! return the pixel associated with an iterator
    healpix::Healpix::Pixel pixel(typename std::vector<C>::const_iterator it)const{
        healpix::Healpix::Pixel px(it-this->begin(), m_hp);
        return px;
    }

    //! @brief access a content object by direction, for modificaion
    C& operator[](const astro::SkyDir& dir){
        healpix::Healpix::Pixel pix = m_hp.pixel(dir);
        return at(pix.index());
    }

    //! brief access a content object in read-only mode
    const C& operator[](const astro::SkyDir& dir)const{
        healpix::Healpix::Pixel pix = m_hp.pixel(dir);
        return at(pix.index());
    }
    //! access the Healpix configuration object
    Healpix healpix()const{return m_hp;}
    void setHealpix(healpix::Healpix hp){m_hp=hp; resize(hp.size());}

private:
    healpix::Healpix m_hp;
};

} // namespace healpix
#endif
