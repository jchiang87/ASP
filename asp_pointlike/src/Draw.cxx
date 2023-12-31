/** @file Draw.cxx
@brief implementation of Draw

$Header$

*/


#include <iomanip>
#include "pointlike/Draw.h"
#include "pointlike/Data.h"

#include "pointlike/PointSourceLikelihood.h"
#include "pointlike/SourceLikelihood.h"

#include "astro/SkyDir.h"

#include "skymaps/SkyImage.h"
#include "skymaps/BinnedPhotonData.h"
#include "skymaps/Band.h"
#include "skymaps/SkySpectrum.h"

using namespace pointlike;
using astro::SkyDir;
using skymaps::BinnedPhotonData;
using skymaps::SkyImage;

namespace pointlike {
  struct lt{
    bool operator()(astro::SkyDir d1, astro::SkyDir d2) const {
      if (fabs(d1.b() - d2.b()) > 1e-5) return (d1.b() < d2.b());
      else return (d1.l() < d2.l());
    }
  };

  typedef std::map<astro::SkyDir, std::vector<double>, pointlike::lt > TSCache;


  /// @class SkyTS
  /// @brief adapt a Binned Photon Data to give TS for bins with given energy
  template <class Likelihood>
  class SkyTS : public astro::SkyFunction {

  private: 
    skymaps::BinnedPhotonData& m_data;
    const skymaps::SkySpectrum& m_background;
    unsigned int m_nenergybins;
    unsigned int m_bin;
    double m_emin;
    double m_minalpha;
    TSCache& m_tsvalues; 
    Likelihood * m_ps;

  public: 
    SkyTS(BinnedPhotonData& data, const skymaps::SkySpectrum& background,
	  TSCache& cache, int energyBin, double minEnergy, double min_alpha):
      m_data(data),
      m_background(background),
      m_nenergybins(0),
      m_bin(energyBin),
      m_emin(minEnergy),
      m_minalpha(min_alpha),
      m_tsvalues(cache){

      for( skymaps::BinnedPhotonData::const_iterator bit = m_data.begin(); 
	   bit!=m_data.end(); ++bit){
	if (bit->emax() < m_emin) continue;
	m_nenergybins++;
//	std::cout << "SkyTS> Added energyBin: " << m_nenergybins << " " 
//		  << bit->emin() << " " << bit->emax() << std::endl;
      }
       Likelihood::set_min_alpha(m_minalpha);
       Likelihood::set_energy_range(m_emin, 1e6);
       Likelihood::set_diffuse(const_cast<skymaps::SkySpectrum*>(&m_background));
       m_ps = new Likelihood(m_data, "test",astro::SkyDir(0,0));
    }

    ~SkyTS() {
       delete m_ps;
    };  

    double operator() (const astro::SkyDir& sd) const {

	if (m_tsvalues.find(sd) == m_tsvalues.end()){


	  m_ps->setDir(sd,false);
	  // 	ps->setup(m_data);
	  m_ps->maximize();

	  double t = m_ps->TS();
	  std::vector<double> ts;
	  ts.push_back(t);
	  for (unsigned int i = 0; i < m_nenergybins; ++i){
	    double e_ts = m_ps->TS(i);
	    double e_alpha = m_ps->alpha(i);
	    if (e_alpha < m_minalpha) e_ts = 0;
	    ts.push_back(e_ts);
// 	      if (e_ts > 0)
// 		std::cout << "Using: " << std::setprecision(2) << e_alpha 
// 			  << " "  << e_ts << " " <<  std::setprecision(0);
	  }
	  m_tsvalues[sd] = ts;

//	    m_ps->printSpectrum();
 	    std::cout << "l="<<sd.l()<<" b="<<sd.b()<<" TS=" << t << std::endl;
// 	    std::cout << "-----" << std::endl;
	  return ts[m_bin];
	} else {
	  return (*m_tsvalues.find(sd)).second[m_bin];
	};
      };
   };
//--------------------------------------------------------------------------------------


}




Draw::Draw(BinnedPhotonData& map, const skymaps::SkySpectrum* background, 
	   bool ts, double eMin, double minalpha, bool sourcelike)
: m_map(map)
, m_background(background)
, m_galactic(true)
, m_zenith(false)
, m_proj("")
, m_exposure(0) // default: do not apply
  , m_layers(1)
  , m_emin(eMin)
  , m_minalpha(minalpha)
  , m_ts(ts)
  , m_sourcelike(sourcelike)
{ pointlike::PointSourceLikelihood::set_energy_range(m_emin, 1e6); }

Draw::Draw(Data& data)
: m_map(data.map())
, m_background(0)
, m_galactic(true)
, m_zenith(false)
, m_proj("")
, m_exposure(0) // default: do not apply
, m_layers(1)
  , m_ts(false)
{}

void Draw::density(const astro::SkyDir& dir, std::string outputFile, double pixel, 
                      double fov, bool smooth, int mincount) {

    std::string proj (fov>90? "AIT":"ZEA");
    if( !m_proj.empty()){ proj = m_proj;}
                
    SkyImage image(dir, outputFile, pixel, fov, m_layers, proj,  m_galactic, m_zenith);

    image.fill(SkyDensity(m_map, smooth, mincount, m_exposure), 0); // PhotonMap is a SkyFunction of the density 

    std::cout 
        <<   "\t minimum "<< image.minimum()
        << "\n\t maximum "<< image.maximum()
        << "\n\t average "<< (image.total()/image.count())
        << std::endl;
		   
};		   
		   

void Draw::TS(const astro::SkyDir& dir, std::string outputFile, double pixel, 
                 double fov, bool smooth, int mincount) {
    std::string proj (fov>90? "AIT":"ZEA");
    if( !m_proj.empty()){ proj = m_proj;}

    int nBins = 0;
    for( skymaps::BinnedPhotonData::const_iterator bit = m_map.begin(); 
	 bit!=m_map.end(); ++bit){
      if (bit->emax() < m_emin) continue;
//      std::cout << "SKYTS>  energy: " << bit->emin() << " " << bit->emax() 
//		<< std::endl;
      ++nBins;
    }

    std::cout << "SkyTS> Constructing SkyImage with: " << nBins+1 << " layers" 
	      << std::endl;
    SkyImage image2(dir, outputFile, pixel, fov, nBins+1, 
		    proj,  m_galactic, m_zenith); 
    TSCache cache;
    for (int i = 0; i <=nBins; ++i){
//      std::cout << " SkyTS> Filling layer: " << i+1 << " emin: " << m_emin << std::endl;
      if(m_sourcelike) image2.fill(SkyTS<SourceLikelihood>(m_map, *m_background, cache, i, m_emin, m_minalpha), i);
      else image2.fill(SkyTS<PointSourceLikelihood>(m_map, *m_background, cache, i, m_emin, m_minalpha), i);
    }
		 
};		 

void Draw::region(const astro::SkyDir& dir, std::string outputFile, double pixel, 
                  double fov, bool smooth, int mincount)
{
    density(dir,outputFile,pixel,fov,smooth,mincount);
    
    if (m_ts && m_background){
      std::string outputTS = outputFile;
      if (outputTS.find(".fits") != std::string::npos)
	outputTS.replace(outputTS.find(".fits"), 0, "_TS");
      else 
	outputTS = std::string("tsvalues.fits");
      TS(dir,outputTS,pixel,fov,smooth,mincount); 
    }

//--------------------------------------------------------------------------------------

    /// @class SkyCount
    /// @brief adapt a BinnedPhotonData to give counts for bins with given energy
    class SkyCount : public astro::SkyFunction {
    public:
        SkyCount(const BinnedPhotonData& data, double energy): 
          m_data(data), m_energy(energy){}

          double operator()(const astro::SkyDir & sd) const {
              double  value = m_data.value(sd, m_energy); 
              return value;    
          }
    private:
        const BinnedPhotonData& m_data;
        double m_energy;
    };
#if 0

    std::cout << "Filling layers "<< layer << " and above with ... ";
    int points(0);
    for (BinnedPhotonData::const_iterator it = m_map.begin();
        it!= m_map.end(); ++it)
    {
        if (it->first.level() >= level) {
            int layer = it->first.level() - m_map.minLevel() + 1;
            if(image.addPoint((it->first)(), it->second, layer)) points+= it->second;
        }
    }
    std::cout <<  points << " hit display pixels" << std::endl;

    for(int layer=1; layer!=m_layers; ++m_layers){
       image.fill(SkyCount(m_map), 100.);
    }
#endif

    std::cout << "Writing image to file \""
        << outputFile << "\""<<std::endl;

}
void Draw::sky(std::string outputfile, double pixel, bool smooth, int mincount)
{
    region(SkyDir(0,0, SkyDir::GALACTIC), outputfile, pixel, 180., smooth, mincount);
}

void Draw::googleSky(std::string outfile, double pixelsize, bool smooth, int mincount)
{
    std::string proj = m_proj;    m_proj = "CAR";
    bool gal = m_galactic; m_galactic = false;
    region(SkyDir(180,0), outfile, pixelsize, 180, smooth, mincount);
    m_proj = proj;
    m_galactic = gal;
}


//-------------------------------------------------------------------
//             SkyDensity methods
//-------------------------------------------------------------------
SkyDensity::SkyDensity(const skymaps::BinnedPhotonData& data, bool smooth, int mincount
                       ,const astro::SkyFunction* exposure)
: m_data(&data)
, m_band(0)
, m_smooth(smooth)
, m_mincount(mincount)
, m_exposure(exposure)
{}

SkyDensity::SkyDensity(const skymaps::Band& band)
: m_data(0)
, m_band(&band)
, m_smooth(false)
, m_mincount(0)
, m_exposure(0)
{}

double SkyDensity::operator()(const astro::SkyDir & sd) const 
{
    double  value;

    if( m_band!=0) {
        // only selected band
        return (*m_band)(sd);
    }

    if (m_smooth)
        value = m_data->smoothDensity(sd, m_mincount);
    else
        value = m_data->density(sd);

    if(m_exposure!=0){
        // note we are not using energy dependence here
        double exposure( (*m_exposure)(sd) );
        if( exposure>0.) value /= exposure;
    }
    return value;    
}
