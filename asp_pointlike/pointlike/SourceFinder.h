/** @file SourceFinder.h
@brief declare class SourceFinder

$Header$
*/

#ifndef pointlike_SourceFinder_h
#define pointlike_SourceFinder_h

//#include "tools/PowerLawFilter.h"
#include "pointlike/Data.h"
#include "skymaps/BinnedPhotonData.h"
#include "pointlike/PointSourceLikelihood.h"
#include "pointlike/Draw.h"

#include "astro/SkyDir.h"

#include "embed_python/Module.h"

#include <vector>
#include <map>
#include <iostream>


namespace pointlike {
    //----------------------------------------------
    /** @class CanInfo

    */


    class CanInfo // Candidate info.  
    {
    public:
        CanInfo(double value = 0, double sigma = 0, 
            astro::SkyDir dir = astro::SkyDir(0,0), int neighbor=-1):
        m_value(value),
            m_sigma(sigma), 
            m_dir(dir), 
            m_2bdeleted(false),
            m_isSource(false),
            m_weighted_count(0),
            m_hasStrongNeighbor(false),
            m_fit(0),
            m_strongNeighbor( neighbor) 
        {
        }

        double value () const {return m_value;}
        double sigma () const {return m_sigma;}
        astro::SkyDir dir () const {return m_dir;}
        double ra() const {return m_dir.ra();}
        double dec() const {return m_dir.dec();}
        bool is2bdeleted () const {return m_2bdeleted;}
        bool isSource () const {return m_isSource;}
        PointSourceLikelihood* fit(){return m_fit;}
        int weighted_count () const {return m_weighted_count;}
        int skipped () const {return m_skipped;}
        bool hasStrongNeighbor() const {return m_hasStrongNeighbor;}
        int strongNeighbor() const {return m_strongNeighbor;}

        void setDelete () {m_2bdeleted = true;}
        void setSource (bool value = true) {m_isSource = value;}
        void set_total_value (double value = 0.0) {m_value = value;}
        void set_sigma (double value = 0.0) {m_sigma = value;}
        void set_dir (astro::SkyDir value = astro::SkyDir(0,0)) {m_dir = value;}
        void set_fit(PointSourceLikelihood* fit){m_fit=fit;}
        void set_skipped (int value = 0) {m_skipped = value;}
        void setHasStrongNeighbor (bool value = true) {m_hasStrongNeighbor = value;}
        void setStrongNeighbor (int value) {m_strongNeighbor = value;}

    private:
        double m_value; ///< TS value.
        double m_sigma; ///< localization sigma
        astro::SkyDir m_dir;
        bool   m_2bdeleted; // True means this is flagged to be deleted later.
        bool   m_isSource;  // True if this corresponds to a confirmed source
        PointSourceLikelihood* m_fit;
        int m_weighted_count; // weighted count of photons in enclosing pixel.  level of enclosing pixel is determined by pointfind_setup.py
        int m_skipped; // number of candidates rejected before this one was accepted.  Count is reset each time a candidate is accepted.
        bool m_hasStrongNeighbor;  // Is there a stronger nearby candidate?
        int m_strongNeighbor;  // Location of strongest nearby candidate.

    }; 

    /**
    @class SourceFinder
    @brief Find point source Candidates in a data field

    */
    class SourceFinder {
    public:

        SourceFinder(pointlike::Data& data);
        ~SourceFinder();

        typedef std::map<int, CanInfo> Candidates;
        typedef std::map<int, pointlike::PointSourceLikelihood > LikelihoodMap;
        typedef std::map<double, CanInfo> Prelim; // Preliminary candidates

        //! Region selection

        /** @brief return modifiable reference to candidates map
        */
        Candidates & getCandidates() {return m_can;}

        /** @brief Analyze range of likelihood significance values for all pixels at a particular level  
        */
        void examineRegion(void) ;


        //! Eliminate neighbors within cone
        void prune_neighbors(void);

        //! summarize results in a ds9 region file
        void createReg(const std::string& filename, double radius = -1.,
            const std::string& color = "white");

        void createTable(const std::string& filename);

        //! allow access to map
        skymaps::BinnedPhotonData& getMap() {return(m_pmap);}

        //! return vector of candidates, copy of current list

        std::vector<CanInfo> candidateList()const;

        //! write contents of CanInfo to fits file
        void createFitsFile(const std::string & outputFile,
            const std::string & tablename="PNTFIND", bool clobber= true) const;

        //! write a reg file
        void createRegFile(std::string filename, std::string color="white", double tsmin=0)const;


        //! run the current set of steps
        void run();

        static void setParameters(const embed_python::Module & module);
    private:
        skymaps::BinnedPhotonData& m_pmap;
        Candidates m_can;
        std::ostream * m_log;
        std::ostream& out(){return * m_log;}
    };



} // namespace tools

#endif


