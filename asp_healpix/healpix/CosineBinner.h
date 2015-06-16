/** @file CosineBinner.h
@brief Define the CosineBinner classixel 

@author T. Burnett

$Header$
*/

#ifndef healpix_CosineBinner_h
#define healpix_CosineBinner_h

#include <vector>
#include <string>

namespace healpix {

    /** @class CosineBinner
        @brief manage a set of bins in cos(theta), and optioinally phi as well

        Note that it inherits from a vector of floats, corresponding to the bins in cos(theta)

    */

class CosineBinner : public std::vector<float> {
public:
    CosineBinner();
    
    /// the binning function: add value to the selected bin, if costheta in range
    void fill(double costheta, double value);
    
    /// the binning function: add value to the selected bin, if costheta in range
    //! alternate version for phi binning.
    //! @param costheta 
    //! @param phi value of phi, radians
    //! @return the index of the bin that was selected
    size_t fill(double costheta, double phi, double value);
    
    /// modifiable reference to the contents of the bin containing the cos(theta) value
    float& operator[](double costheta);
    const float& operator[](double costheta)const;

    /// reference to the contents of the bin containing the cos(theta) value
    //! version that has phi as well (operator() allows multiple args)
    //! @param costheta cos(theta)
    //! @param phi [-1] phi angle in radians: if negative, ignore and return average
    const float& operator()(double costheta, double phi=-1)const;

    /// cos(theta) for the iterator
    double costheta(std::vector<float>::const_iterator i)const;

    /// phi for the iterator
    double phi(std::vector<float>::const_iterator i) const;

    const_iterator end_costh()const{return begin()+nbins();}


    /// integral over the range with functor accepting costheta as an arg. 
    template<class F>
    double operator()(const F& f)const
    {   
        double sum=0;
        int n(0);
        for(const_iterator it=begin(); it!=end_costh(); ++it, ++n){
            sum += (*it)*f(costheta(it));
        }
        return sum; 

    }
                           
    /// integral over the range with functor accepting costheta, phi as args. 
    template<class G>
    double integral(const G& f)const
    {   
        double sum=0;
        for(const_iterator it=end_costh(); it!=end(); ++it){
            sum += (*it)*f.integral(costheta(it), phi(it) );
        }
        return sum; 

    }



    /// define the binning scheme with class (static) variables
    static void setBinning(double cosmin=0., size_t nbins=40, bool sqrt_weight=true);

    //! set phibins to enable binning in phi
    //! phibins [15] note default is 3 degrees per bin, since folded about 0-45 degrees.
    static void setPhiBins(size_t phibins=15);

    static std::string thetaBinning();
    static double cosmin();
    static size_t nbins();
    static size_t nphibins();

    //! access to fundamental binning
    static size_t cosine_index(double costheta);
    static size_t phi_index(double phi);

    //! the translation from 0-2pi to 0-pi/4
    static double folded_phi(double phi);

private:


    static double s_cosmin; ///< minimum value of cos(theta)
    static size_t s_nbins;  ///< number of costheta bins
    static bool  s_sqrt_weight; ///< true to use sqrt function, otherwise linear
    static size_t s_phibins; ///< number of phi bins
};

}
#endif
