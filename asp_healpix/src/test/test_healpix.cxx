/** @file test_healpix.cxx
@brief Test program for various healpix routines

@author M. Roth, T. Burnett

$Header$
*/

#include "healpix/Map.h"
#include "src/base/message_error.h"
#include "healpix/HealPixel.h"
#include "TestHealpix.h"
#include "TestHealpixArray.h"
#include "facilities/commonUtilities.h"
#include "healpix/CosineBinner.h"
#include "healpix/HealpixArrayIO.h"
#include <iostream>
#include <string>
#include <sstream>
#include <stdexcept>
using namespace std;
using namespace healpix;
#include <cmath>

namespace {

    // used to test CosineBinner below
    class Funct{
    public:
        Funct(int power=0): p(power){}
        double operator()(double z )const{return p==0?1.: std::pow(1.-z,p);}
    int p;
    };

        // used to test CosineBinner below
    class PhiFunct{
    public:
        PhiFunct(int power=0): p(power){}
        double integral(double z, double phi )const{return p==0?1.: std::pow(1.-z,p);}
    int p;
    };
}

int main() {

    int rc = 0;
    try {
#if 0
        int i=6;//for(int i =6;i<=11;i++)
        //Map and filter test
        {
            stringstream oss;
            oss << i;
            string num(oss.str());
            cout << "Reading fits file "+num+"...";
            
            std::string filename=facilities::commonUtilities::joinPath(facilities::commonUtilities::getDataPath("healpix"), "srctest.fits"); 

            Map<double> mp(filename,i);
            cout << "done!" << endl;
            cout << "Filtering map...";
            mp.mfcn(155*(2*(i-5)),100*pow(2.35,(i-6)*1.));
            cout << "done!" << endl;
            //cout << "Writing output fits file...";
            //if the output file already exists, then the program will throw an error
            //mp.writemap(string("mfv_l"+num+".fits"));
            cout << "done!" << endl;
        }
        // HealPixel test
        {
            if( ! HealPixel::test() ) {
                ++rc; std::cerr << "Fail HealPixel test";
            }
            HealPixel h33=HealPixel(0,3);
            std::vector<HealPixel> neighbors = h33.neighbors();
            std::cout << "Neighbors of HealPixel(0,3): ";
            for( std::vector<HealPixel>::const_iterator it = neighbors.begin(); it!=neighbors.end(); ++it){
                std::cout << it->index() << ", ";
            }
            std::cout << endl;
        }

        TestHealpix();
        TestHealpixArray();
#endif
        // CosineBinner test
        {
            CosineBinner::setBinning(0,40, true); // default
            CosineBinner cb;

            size_t s = cb.size(); // test
            size_t ss = cb.end() - cb.begin();

            double delta(0.01);
            for( double z(delta/2.); z<=1.0; z+=delta){
                cb.fill(z, delta);
            }
            double test0 ( cb( Funct())-1 ), test1( cb(Funct(1))-0.5), test2( cb(Funct(2))-0.25);
            std::cout << "CosineBinner tests: " << test0<<", " << test1<<", " << test2 << std::endl;
            //CosineBinner tests: -0.01, -0.00612501, 0.0781047
            //CosineBinner tests(400): -2.23517e-008, -0.000260449, 0.0829861

            // now run through phi for given theta: first set phi binning static
            CosineBinner::setPhiBins(15);
            size_t sss = cb.end_costh() - cb.begin();
            // now an object should be larger
            CosineBinner cbphi;
            size_t i( CosineBinner::phi_index((22.5+90.)*M_PI/180.) ); // should be 7
            double deltaphi(M_PI/180.); // 1 degree step
            double z2(0.9); 
            for( double phi(deltaphi/2.); phi<2*M_PI; phi+=deltaphi){

                size_t j = cbphi.fill(z2, phi, 1.);
                double tphi( cbphi.phi(cbphi.begin()+j) );
                double delta_phi( CosineBinner::folded_phi(phi)* M_PI/4 -tphi);
                if( fabs(delta_phi)*180/M_PI > 1.5 ){
                    std::cout << "fail phi binning test" << std::endl;
                    std::cout  <<  phi*180/M_PI << ", " << j <<", "<< delta_phi*180/M_PI << std::endl;
                    rc=1;
                    break;
                }



            }
            double fphi( cbphi.integral(PhiFunct()));
            double full( cbphi(Funct()) );
            if( fphi!= 360. || full != 360.){
                std::cout << "fail phi integtral test" << std::endl;
                std::cout << "...with, without phi: " << fphi << ", " << full<< std::endl;
                rc=1;
            }

            // now check I/O
            //HealpixArrayIO& hpio = HealpixArrayIO::instance();
            //HealpixArray<CosineBinner> 
            //hpio.write(cbphi, "test.fits", "COSINEBINS");



        }

    }
    catch (const Message_error & error) {
        std::cout << error.what() << std::endl;
        rc =1;
    }
    catch (const exception& e) {
        cerr << "Failed test because caught " <<typeid(e).name()<<" \""  
            << e.what() << "\"" << endl;
        rc= 1;
    }
    return rc;
}
