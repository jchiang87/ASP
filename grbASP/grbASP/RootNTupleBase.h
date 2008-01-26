/**
 * @file RootNTupleBase.h
 * @brief Provide fast vector access to columns in a ROOT ntuple.
 *
 * @author J. Chiang
 *
 * $Header$
 */

#ifndef grbASP_RootNTupleBase_h
#define grbASP_RootNTupleBase_h

#include <map>
#include <string>
#include <vector>

class TFile;
class TTree;

namespace grbASP {

class RootNTupleBase {

public:
   
   RootNTupleBase(const std::string & rootFile,
                  const std::string & treeName,
                  const std::vector<std::string> & 
                  leafNames=std::vector<std::string>(0));

//   const std::vector<double> & operator[](const std::string & leafName) const;

   const std::vector<std::string> & leafNames() const {
      return m_leafNames;
   }

   const std::vector<std::string> & leafTypes() const {
      return m_leafTypes;
   }

private:

   TFile * m_rootFile;
   TTree * m_tree;

   std::map<std::string, std::vector<double> > m_columns;

   std::vector<std::string> m_leafNames;
   std::vector<std::string> m_leafTypes;
   
   void readLeafTypes();
   void readLeafNames();

};

} // namespace grbASP

#endif // grbASP_RootNTupleBase_h
