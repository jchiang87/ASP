/** @file TestHealpix.h
@brief code to test the class Healpix

$Header$

*/

#include "healpix/Healpix.h"

#include "facilities/commonUtilities.h"
#include <algorithm>
#include <iomanip>
#include <stdexcept>
#include <fstream>



// simple insertion operator to print a vector<int> object
std::ostream& operator<<(std::ostream& out, const std::vector<int> v)
{

    for (std::vector<int>::const_iterator it = v.begin(); it < v.end(); ++it)
    {
        out << *it << "\t";
    }
    out << std::endl;
    return out;
}

class TestHealpix {
public:
    TestHealpix(){
        using healpix::Healpix;
        test(256, healpix::Healpix::NESTED, astro::SkyDir::GALACTIC);
//        test(256, Healpix::NESTED, astro::SkyDir::EQUATORIAL);
//        test(256, Healpix::RING, astro::SkyDir::GALACTIC);
//        test(256, Healpix::RING, astro::SkyDir::EQUATORIAL);
        
        Healpix hp(8);
        TestNeighbors(hp);
    }
    void test(long nside, healpix::Healpix::Ordering ord, astro::SkyDir::CoordSystem coord)
    {
        using healpix::Healpix;

        // create basic Healpix object to define the pixelization level nside
        Healpix hp(nside, ord, coord);

        std::cout << "\nCreated a " << (hp.nested()? "NESTED":"RING") 
            << " Healpix object with " << hp.npix() << " pixels"  
            << " (nside="<<hp.nside()<<")"
            << " in " << (hp.galactic()? "GALACTIC":"EQUATORIAL") << " coords"<< std::endl;

#if 0
        // make a table of index, ra, dec 
        std::cout << "Table of index, ra, dec" << std::endl;
        std::copy(hp.begin(), hp.end() , std::ostream_iterator<Healpix::Pixel>(std::cout, "\n") );
        std::cout << "done" << std::endl;
#endif
        // test use of for_each, and apply test to each pixel
        std::cout << "\nTesting pixels...";
        std::for_each(hp.begin(), hp.end(), TestPixel(hp));
        std::cout << "done!"<< std::endl;
        // test doing an integral
        std::cout << "\nTesting integral with even powers of cos(theta)\n"
            << "n\tintegral/4PI\texpect\t\t relative error\n";
        for( int i =2; i<6; i+=2){
            double integral = hp.integrate(CosinePower(i))/(4.*M_PI),
                expect = ((i&1)==1)? 0 : 1./(i+1.);
            std::cout << i << "\t" 
                << std::setiosflags(std::ios_base::scientific) << std::setprecision(6)
                << std::setw(10) << integral
                << std::setw(15) << expect
                << std::setw(12) << std::setprecision(1)<< integral/expect -1
                << std::endl;
            if( fabs(integral-expect)> 1e-6) throw std::runtime_error("Failed integration test"); 

        }
    }


    class TestPixel {
    public:
        TestPixel(const healpix::Healpix& hp):m_hp(hp){}

        void operator()(const healpix::Healpix::Pixel& pix)
        {
            astro::SkyDir dir=pix; // behaves like a SkyDir
            healpix::Healpix::Pixel p2(dir,m_hp);
            if( p2.index() != pix.index() ){
                throw std::runtime_error("index mismatch");
            }
        }
        const healpix::Healpix& m_hp;
    };

    /// functor to try powers of cos(theta)
    class CosinePower : public astro::SkyFunction {
    public:
        CosinePower(int n): m_n(n){}
        double operator()(const astro::SkyDir& dir)const
        {
            double costheta = dir().z();
            return ::pow(costheta, m_n);
        }
        int m_n;
    };

    void TestNeighbors(const healpix::Healpix & hp)
    {
        typedef std::map<long, long> SORTMAP;
        std::cout << "\nTesting neighbors logic...";
        std::string filename=facilities::commonUtilities::joinPath(facilities::commonUtilities::getDataPath("healpix"),
            "Healpix Neighbors Nside=8.txt");
        std::ifstream f( filename.c_str() ); // File provided by Healpix developers
           
        for (healpix::Healpix::Iterator it = hp.begin(); it < hp.end(); ++it)
        {
            // std::cout << "Checking neighbors for pixel " << (*it).index() << std::endl;
            std::vector<healpix::Healpix::Pixel> pv;
            (*it).neighbors(pv);  // Get neighbors as vector of pixels
            
            // Convert to vector of integers
            std::vector<int> calculated;
            for(std::vector<healpix::Healpix::Pixel>::iterator it2 = pv.begin();
                it2 != pv.end(); ++it2)
            {
                calculated.push_back(it2->index());
            }
            
            // Get entry from file 
            long pixel_nbr;
            f >> pixel_nbr;  
            if( pixel_nbr > hp.npix() ) { 
                std::cout << "warning, quit since pixel number read from file is >" << hp.npix() << std::endl;
                break;
            }
            std::vector<int> from_file;
            for (int i = 0; i < 8; i++)
            {
                int neighbor;
                f >> neighbor;
                if (neighbor >= 0)
                    from_file.push_back(neighbor);
            }
            
            #if 0 // Run this block to see detailed results.
            {
                std::cout << calculated << from_file << std::endl ;
            }
            #endif

            if (calculated != from_file)
            {
                std::cout << "Neighbor mismatch for pixel " << pixel_nbr << std::endl;
                std::cout << "expected: " << from_file << "\n  found:" << calculated << std::endl;
                throw std::runtime_error("Healpix test failed");
            }
            #if 0 // Run this block to see detailed results.
            {
                std::cout << calculated << from_file << std::endl ;
            }
            #endif
        }
        std::cout << "Done.\n";
    }
};
