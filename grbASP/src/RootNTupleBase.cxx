/**
 * @file RootNTupleBase.cxx
 * @brief Provide fast vector access to columns in a ROOT ntuple.
 *
 * @author J. Chiang
 * 
 * $Header$
 */

#include <iostream>

#include "TFile.h"
#include "TTree.h"
#include "TLeaf.h" 
#include "TObjArray.h"
#include "TObject.h"
#include "TEventList.h"

#include "grbASP/RootNTupleBase.h"

namespace grbASP {

RootNTupleBase::RootNTupleBase(const std::string & rootFile,
                               const std::string & treeName,
                               const std::vector<std::string> & leafNames)
   : m_rootFile(TFile::Open(rootFile.c_str())), 
     m_tree((TTree *)(m_rootFile->Get(treeName.c_str()))) {
   readLeafNames();
   readLeafTypes();
}

void RootNTupleBase::readLeafNames() {
   std::vector<TObject *> branches;

   TObjArray * branchList(m_tree->GetListOfBranches());
   size_t ncols(branchList->GetEntries());
   
   for (size_t i(0); i < ncols; i++) {
      branches.push_back(branchList->At(i));
      m_leafNames.push_back(branches[i]->GetName());
   }
}

void RootNTupleBase::readLeafTypes() {
   m_leafTypes.clear();
   TObjArray * leaves(m_tree->GetListOfLeaves());
   if (!leaves) {
      return;
   }
   UInt_t numLeaves(leaves->GetEntries());

   for (UInt_t iLeaf(0); iLeaf < numLeaves; iLeaf++) {
      m_leafTypes.push_back( 
         std::string(((TLeaf*)leaves->At(iLeaf))->GetTypeName()) );
   }
}

void RootNTupleBase::readTree(const std::vector<std::string> & colNames,
                              const std::string & filterString) {
   
// Allocate space for row data.  Double_t should be sufficent.
   size_t ncols(colNames.size());
   void * values;
   values = new Double_t[ncols];
   
// Set branch addresses for each column name.
   size_t i(0);
   std::vector<std::string>::const_iterator name(colNames.begin());
   std::vector<std::string>
   for ( ; name != colNames.end(); name++


}

} // namespace grbASP
