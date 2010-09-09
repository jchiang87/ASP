
/** @file TestHealpixArrayr.h
@brief test class for HealpixArray

$Header$


*/
#include "healpix/HealpixArray.h"
#include "healpix/Healpix.h"
#include <iostream>
#include <numeric> 
#include <iostream>


    std::ostream& operator<<(std::ostream& out, const astro::SkyDir& dir){
    out << "("<<dir.ra() << ", "<< dir.dec()<< ") ";
    return out;
}

class TestHealpixArray {
public:



    TestHealpixArray(std::ostream& out= std::cout){

        using astro::SkyDir;
        using healpix::Healpix;
        using healpix::HealpixArray;
        // test Healpix array
        int nside = 64;
        out << "\ntesting HealpixArray<int> with nside="<< nside << std::endl;
        Healpix hp(nside);
        HealpixArray<int> hpa(hp);

        // create a SkyDir object, and something to add to it.
        SkyDir d(10,10);
        int toadd = 99;
        hpa[d] += toadd;
        int total = std::accumulate(hpa.begin(), hpa.end(), 0);
        out << "Contents of bin at ra, dec="<< d << " is " 
            << hpa[d] << ", total is " << total <<std::endl;
        out << "direction of first pixel: " <<  hpa.dir(hpa.begin()) << std::endl;
        if( hpa[d] != toadd || total !=toadd )
            throw std::runtime_error("TestHealpixArray failed: see output");
    }
};
