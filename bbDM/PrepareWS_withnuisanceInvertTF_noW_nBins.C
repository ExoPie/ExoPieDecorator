#include <iostream>
#include "RooFormulaVar.h"
#include "RooArgList.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooConstVar.h"
#include "RooChebychev.h"
#include "RooAddPdf.h"
#include "RooWorkspace.h"
#include "RooPlot.h"

// To be added ,
// all the gaussian constraints should be within -1 and 1 sigma  OR 0 to 1 sigma NOT 5 sigma.
// fix TF stats
// fix other systematics
// access systematics via histograms from the .root file so that there is no confusion.

using namespace RooFit ;



/*
PrepareWS.C  Package to build statistical fitting model for background estimation and limit extraction
Author: Raman Khurana
Date:   26-September-2018
V0:     Simple implementation of the model using transfer factors
*/


/*

naming convention: h_region_ process,

e.g.

bincontent: bincontents_sr1_wjets

Histogram:  h_sr1_data, h_sr2_wjets, h_wenu_wjets

Histogram Transfer Factor: htf_

datahist:  use dh_wenu_wjets

RooRealVar: rrv_wenu_wjets
RooRealVar: rrvbc_wenu_wjets (for boncontent)

RooArgList: ral_wenu_wjet s
RooArgList: ralbc_wenu_wjets (for the bin content)

RooParamHist: rph_wenu_wjets

RooAddition: rph_norm_wenu_wjets

RooFormulaVar: rfv_

RooFormulaVar:
*/

//gInterpreter->GenerateDictionary("vector<RooFormulaVar>","RooFormulaVar.h;vector");

TFile* OpenRootFile(TString filename, TString mode="READ"){
  TFile* f = new TFile (filename, mode);
  return f;
}


std::vector<float> GetBinContents(TH1F* h){
  std::vector<float> bcs;
  bcs.clear();
  std::cout<<" histogram name :"<<h->GetName()<<std::endl;
  int nbinsx = h->GetNbinsX();
  for (auto ibin=1; ibin<=nbinsx; ibin++){
    bcs.push_back(h->GetBinContent(ibin));
  }

  return bcs;

}




void addTemplate(RooWorkspace& ws,  RooArgList& vars, TH1F* hist, TString outhistnamestat="") {
  std::cout<<" name = "<<hist->GetName()<<std::endl;
  // this if is for debugging
  //if (TString(hist->GetName())=="bbDM2017_2b_SR_bkgSum"){
  //  hist->Scale((1729/hist->Integral()));
  // }
  if (outhistnamestat.IsNull()){
    outhistnamestat=hist->GetName();
  }
  RooDataHist rhist(outhistnamestat, outhistnamestat,  vars, hist);
  std::cout<<" integral of the histogram for "<<hist->GetName()<<" is "<<rhist.sumEntries()<<"  "<<hist->Integral()<<" bins: "<<hist->GetNbinsX()<<std::endl;

  for (int ibin=1; ibin<hist->GetXaxis()->GetNbins()+1 ;ibin++){
    if (hist->GetBinContent(ibin)<=0) std::cout<<" histogram: "<<hist->GetName()<<" has negative bin content"<<ibin<<" "<<hist->GetBinContent(ibin)<<endl;
    //std::cout<<" binning histogram: "<<hist->GetName()
    //	     <<" ibin: "<<ibin
    //	     <<" lowedge: "<<hist->GetBinLowEdge(ibin)
    //	     <<" bin content "<<hist->GetBinContent(ibin)
    //	     <<std::endl;
  }
  ws.import(rhist);
}


// This function is overloaded
std::vector <RooRealVar> GetRooRealVar(std::vector<float>  bcs, TString name, TString year=""){
  std::vector<RooRealVar> rrvV_ ;
  rrvV_.clear();
  TString postfix;

  for (auto i=0; i<bcs.size(); i++){
    postfix.Form("%d", i+1);
    // fix the naming here using some automation  and also in the next function

    //std::cout<<" name inside GetRooRealVar = "<<name+postfix<<std::endl;
    rrvV_.push_back(RooRealVar(name+postfix+"_"+year,"Background yield in signal region, bin 1", bcs[i], 0.2*bcs[i], 2*bcs[i]));

  }

  return rrvV_;
}

void plotTFPrefit(){

}

void plotSystPrefit(){

}


std::vector<TH1F*> h_vec_tf;
//TFile* f_TF = new TFile("TF_v17_12-00-03_1bMET_2bCTS.root","READ");

std::vector<std::string> createnuisance(float value_,int  nbins, int nuisanceCounter){
  std::vector<std::string> logN_nuisance_vec;
  logN_nuisance_vec.clear();
  for (int i=0; i<nbins; i++){
    TString logN_nuisance_1bin;
    TString value_str;
    value_str.Form("%f",value_);
    TString nuisanceCounter_str;
    nuisanceCounter_str.Form("%d",nuisanceCounter);
    logN_nuisance_1bin = "TMath::Power(1+"+value_str+",@"+nuisanceCounter_str+")";   // this gives a string like  "TMath::Power(1+0.15,@0)"
    logN_nuisance_vec.push_back(std::string(logN_nuisance_1bin));
  }

  return logN_nuisance_vec;
}

std::vector<std::string> createnuisance(std::vector<float> value_,int  nbins, int nuisanceCounter){
  std::vector<std::string> logN_nuisance_vec;
  logN_nuisance_vec.clear();
  for (int i=0; i<nbins; i++){
    TString logN_nuisance_1bin;
    TString value_str;
    value_str.Form("%f",value_[i]);
    TString nuisanceCounter_str;
    nuisanceCounter_str.Form("%d",nuisanceCounter);
    logN_nuisance_1bin = "TMath::Power(1+"+value_str+",@"+nuisanceCounter_str+")";   // this gives a string like  "TMath::Power(1+0.15,@0)"
    logN_nuisance_vec.push_back(std::string(logN_nuisance_1bin));
  }

  return logN_nuisance_vec;
}




/* createRegion parameters are following
1: roorealvar, here it is met
2: background histogram in signal region
3: background histogram in CR
4: data histogram in signal region
5: workspace
6: string to save names etc, as per convention, region_proc for the CR
7: string to save names etc, as per convention, region_proc for the SR
8: output file
9: nuisIndex: index of nuisance to be used from the global nuisance list defined above
10: full list of nuisanceNames
11. full of of nuisanceValues
12. analysis category, merged/resolved: to ensure the difference in the names of TF and other variables in the workspace. Otherwise they will become corelated across merged and resolved category which we don;t want to do.

*/
void createRegion(RooRealVar met, TH1F* h_sr_bkg , TH1F* h_cr_bkg,
		  TH1F* h_sr_data, RooWorkspace& wspace,
		  TString region_proc_cr, TString region_proc_sr, TFile* fOut,
		  std::vector<int> nuisIndex, std::vector<TString> nuisanceName,
		  std::vector<float> nuisanceValue,
		  TString anacat_,
		  TString year_,
		  TFile* fIn_,
		  TString crname){

  TString anacat_orig=anacat_;
  anacat_ = "_"+anacat_;
  RooArgList vars(met);

  /* Get the bin content of each bin of the histogram in a vector which can be used later */
  std::vector<float> bincontents_sr_bkg = GetBinContents(h_sr_bkg);

  // This will create the RooRealVar with 0 to 10*bin content  range.
  // The bkg contribution in SR is RooRealVar and then converted to RooArgList

  // create a vector of RooRealVar, this is needed because I didn't find  way to retrive the RooRealVar back from the RooArgList
  std::vector<RooRealVar> rrvbc_sr_bkg = GetRooRealVar(bincontents_sr_bkg, "rrvbc_"+region_proc_sr+anacat_, year_);

  int nHistbins=bincontents_sr_bkg.size();

  RooArgList ralbc_sr_bkg; // this can be converted to a for loop
  ralbc_sr_bkg.add(rrvbc_sr_bkg[0]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[1]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[2]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[3]);
  // following code is to be extend
  if (nHistbins>=5)   ralbc_sr_bkg.add(rrvbc_sr_bkg[4]);
  if (nHistbins>=6)   ralbc_sr_bkg.add(rrvbc_sr_bkg[5]);
  if (nHistbins>=7)   ralbc_sr_bkg.add(rrvbc_sr_bkg[6]);
  if (nHistbins>=8)   ralbc_sr_bkg.add(rrvbc_sr_bkg[7]);

  if (nHistbins>=9)   ralbc_sr_bkg.add(rrvbc_sr_bkg[8]);
  if (nHistbins>=10)   ralbc_sr_bkg.add(rrvbc_sr_bkg[9]);
  if (nHistbins>=11)   ralbc_sr_bkg.add(rrvbc_sr_bkg[10]);
  if (nHistbins>=12)   ralbc_sr_bkg.add(rrvbc_sr_bkg[11]);


  // Create a RooParametericHist which contains those yields, last argument is just for the binning, we can use the data TH1 for that
  // RPH for the bkg yield in the SR
  RooParametricHist rph_sr_bkg("rph_"+region_proc_sr+anacat_+"_"+year_, " "+region_proc_sr+" PDF in signal region "+anacat_+year_,met,ralbc_sr_bkg, *h_sr_data);


  // Always include a _norm term which should be the sum of the yields (thats how combine likes to play with pdfs)
  // not sure yet why is this needed?
  RooAddition rph_sr_bkg_norm("rph_"+region_proc_sr+anacat_+"_"+year_+"_norm","Total Number of events from background in signal region "+anacat_+year_,ralbc_sr_bkg);


  wspace.import(rph_sr_bkg);
  wspace.import(rph_sr_bkg_norm,RooFit::RecycleConflictNodes());

  std::cout<<" rph for bkg in SR is imported in the WS"<<std::endl;


  /*
    For the control region, the background process will be dependent on the yields of the background in the signal region using a transfer factor.
    The transfer factor TF must account for acceptance/efficiency etc differences in the signal to control regions.
    In this case we define the transfer factor as: ratio of the WJets (electron) yield in the WJets control region and
    WJets in the Signal region.

    For each bin a transfer factor is calculated and the nuisance parameters are associated with this.

    We could imagine that the transfer factor could be associated with some uncertainty - lets say a 1% uncertainty due to efficiency and 2% due to acceptance.
    We need to make nuisance parameters ourselves to model this and give them a nominal value of 0.
  */

  /*
  We need to make the transfer factor a function of these parameters since variations in these uncertainties will lead to variations of the transfer factor. Here we've assumed Log-normal effects (i.e the same as putting lnN in the CR datacard) but we could use any function which could be used to parameterise the effect - eg if the systematic is due to some alternate template, we could use polynomials for example.
  */


  // check the anme and integral of bkg histogram in CR
  std::cout<<" h_cr_bkg: "<<h_cr_bkg->GetName()<<" "<<h_cr_bkg->Integral()<<std::endl;


  // create roodatahist of the background histogram in CR.
  RooDataHist dh_cr_bkg("dh_"+region_proc_cr+anacat_+"_"+year_,"dh_"+region_proc_cr+anacat_+"_"+year_, vars, h_cr_bkg);

  // another copy fo the wjets in wenu CR for division and saving thr TFs central value.
  // transfer factor is defined as ratio of TF =  bkg in CR / bkg in SR

  std::cout<<" datahist created "<<h_cr_bkg->GetName()<<" "<<h_sr_bkg->GetName()
	   <<" "<<h_cr_bkg->GetNbinsX()<<" "<<h_sr_bkg->GetNbinsX()<<std::endl;

  // --- This is the transfer factor used untill now, From 8th Feb 2021 inverted TF are used.
  //TH1F* htf_cr_bkg = (TH1F*) h_cr_bkg->Clone();
  //htf_cr_bkg->Divide(h_sr_bkg);

  // ---  Inverted Transfer factor. later the multiplication is also changed.
  TH1F* htf_cr_bkg = (TH1F*) h_sr_bkg->Clone();
  htf_cr_bkg->Divide(h_cr_bkg);



  // writing this to the root file for presentation purpose.
  h_vec_tf.push_back(htf_cr_bkg);

  /*
  std::cout<<" ratio "<< htf_cr_bkg->GetBinContent(1)
	   <<" "<<htf_cr_bkg->GetBinContent(2)
	   <<" "<<htf_cr_bkg->GetBinContent(3)
	   <<" "<<htf_cr_bkg->GetBinContent(4)
	   <<std::endl
	   <<"  SR yield =" <<h_sr_bkg->GetBinContent(1)
	   <<" "<<h_sr_bkg->GetBinContent(2)
	   <<" "<<h_sr_bkg->GetBinContent(3)
	   <<" "<<h_sr_bkg->GetBinContent(4)
	   <<std::endl
	   <<" "<<h_cr_bkg->GetBinContent(1)
	   <<" "<<h_cr_bkg->GetBinContent(2)
	   <<" "<<h_cr_bkg->GetBinContent(3)
	   <<" "<<h_cr_bkg->GetBinContent(4)
	   <<std::endl   ;

  */
  // Get bin content of each bin of this ratio histogram and save it in the RooRealVar which will be used later for the Actual Transfer Factor with effect of Nuisance parameters included
  // idelaly each of these rooreal var in following vector should be setConstat(1) otherwise it may be treated as free parameter however it should be fixed.
  std::vector <float> bincontents_htf_cr_bkg =  GetBinContents(htf_cr_bkg);

  RooRealVar tf1 ("tf1_"+region_proc_cr+anacat_+"_"+year_,"tf1_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[0]) ;
  RooRealVar tf2 ("tf2_"+region_proc_cr+anacat_+"_"+year_,"tf2_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[1]) ;
  RooRealVar tf3 ("tf3_"+region_proc_cr+anacat_+"_"+year_,"tf3_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[2]) ;
  RooRealVar tf4 ("tf4_"+region_proc_cr+anacat_+"_"+year_,"tf4_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[3]) ;

  // -- Following code is to extend the number of bins
  /*RooRealVar tf5 ("tf5_"+region_proc_cr+anacat_+"_"+year_,"tf5_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[4]) ;
  RooRealVar tf6 ("tf6_"+region_proc_cr+anacat_+"_"+year_,"tf6_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[5]) ;
  RooRealVar tf7 ("tf7_"+region_proc_cr+anacat_+"_"+year_,"tf7_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[6]) ;
  RooRealVar tf8 ("tf8_"+region_proc_cr+anacat_+"_"+year_,"tf8_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[7]) ;

  RooRealVar tf9  ("tf9_"+region_proc_cr+anacat_+"_"+year_, "tf9_"+region_proc_cr+anacat_+year_, bincontents_htf_cr_bkg[8]) ;
  RooRealVar tf10 ("tf10_"+region_proc_cr+anacat_+"_"+year_,"tf10_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[9]) ;
  RooRealVar tf11 ("tf11_"+region_proc_cr+anacat_+"_"+year_,"tf11_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[10]) ;
  RooRealVar tf12 ("tf12_"+region_proc_cr+anacat_+"_"+year_,"tf12_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[11]) ;
  */

  // at this moment keeping this code here for add systematics on the TF,
  // considered only two nuisances, will complete the list later on, once i know which other nuisances has to be here
  // at least working template is here, not only string has to be added to the vector to add a new nuisance


  /*
  std::vector<TString> systematic_vector;
  systematic_vector.clear();
  systematic_vector.push_back("jec"); systematic_vector.push_back("btagweight");


  std::vector<TString> variation;
  variation.clear();
  variation.push_back("up"); variation.push_back("down");
  */


  // ------ all the nuisances log N has to be added before creating RooFormulaVar of the Transfer Factors.
  // ------ adding nuisance by hand, magnitue of each bin can be different as in the e.g. below


  std::vector<float> tf_stats_err_vector;   tf_stats_err_vector.clear();
  // updated stats error from root file
  TString stats_err_hist_name = anacat_orig+"/"+crname+"/"+"allbin";
  std::cout<<" ---------------- stats_err_hist_name: "<<stats_err_hist_name<<std::endl;
  TH1F* stats_error_ = (TH1F*)fIn_->Get(stats_err_hist_name);
  tf_stats_err_vector.push_back(stats_error_->GetBinContent(1));
  tf_stats_err_vector.push_back(stats_error_->GetBinContent(2));
  tf_stats_err_vector.push_back(stats_error_->GetBinContent(3));
  tf_stats_err_vector.push_back(stats_error_->GetBinContent(4));

  // following code is to be extend
  if (nHistbins>=5 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(5));
  if (nHistbins>=6 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(6));
  if (nHistbins>=7 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(7));
  if (nHistbins>=8 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(8));


  if (nHistbins>=9 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(9));
  if (nHistbins>=10 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(10));
  if (nHistbins>=11 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(11));
  if (nHistbins>=12 ) tf_stats_err_vector.push_back(stats_error_->GetBinContent(12));


  /*
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(1) / htf_cr_bkg->GetBinContent(1) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(2) / htf_cr_bkg->GetBinContent(2) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(3) / htf_cr_bkg->GetBinContent(3) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(4) / htf_cr_bkg->GetBinContent(4) ) ;


  if (nHistbins>=5 ) tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(5) / htf_cr_bkg->GetBinContent(5) ) ;
  if (nHistbins>=6 ) tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(6) / htf_cr_bkg->GetBinContent(6) ) ;
  if (nHistbins>=7 ) tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(7) / htf_cr_bkg->GetBinContent(7) ) ;
  if (nHistbins>=8 ) tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(8) / htf_cr_bkg->GetBinContent(8) ) ;
  */

  /*
  std::cout<<" tf stats errors "
	   <<" "<<tf_stats_err_vector[0]
	   <<" "<<tf_stats_err_vector[1]
	   <<" "<<tf_stats_err_vector[2]
	   <<" "<<tf_stats_err_vector[3]
	   <<" "<<tf_stats_err_vector[4]
	   <<" nHistbins: "<<nHistbins
	   <<std::endl;
  */


  int syst_counter = 0;

  TString rfv_bin1 = Form("@%d*",syst_counter++); // this is transfer factor  ,  ++ is needed so that the counter is increamented automatically after its usage
  TString rfv_bin2 = rfv_bin1; // yes this is correct: this is to write @0 for each bin and at next occurenace it will become @1 and so on,
  TString rfv_bin3 = rfv_bin1;
  TString rfv_bin4 = rfv_bin1;
  // following code is to be extend
  /*TString rfv_bin5 = rfv_bin1;
  TString rfv_bin6 = rfv_bin1;
  TString rfv_bin7 = rfv_bin1;
  TString rfv_bin8 = rfv_bin1;

  TString rfv_bin9 = rfv_bin1;
  TString rfv_bin10 = rfv_bin1;
  TString rfv_bin11 = rfv_bin1;
  TString rfv_bin12 = rfv_bin1;
  */


  std::vector<std::string> rfv_tf_stats_err_vector = createnuisance(tf_stats_err_vector, nHistbins, syst_counter++);

  rfv_bin1  += rfv_tf_stats_err_vector[0] ;
  rfv_bin2  += rfv_tf_stats_err_vector[1] ;
  rfv_bin3  += rfv_tf_stats_err_vector[2] ;
  rfv_bin4  += rfv_tf_stats_err_vector[3] ;
  //following code is to be extend
  /*if (nHistbins>=5 )   rfv_bin5  += rfv_tf_stats_err_vector[4] ;
  if (nHistbins>=6 )   rfv_bin6  += rfv_tf_stats_err_vector[5] ;
  if (nHistbins>=7 )   rfv_bin7  += rfv_tf_stats_err_vector[6] ;
  if (nHistbins>=8 )   rfv_bin8  += rfv_tf_stats_err_vector[7] ;

  if (nHistbins>=9 )    rfv_bin9   += rfv_tf_stats_err_vector[8] ;
  if (nHistbins>=10 )   rfv_bin10  += rfv_tf_stats_err_vector[9] ;
  if (nHistbins>=11 )   rfv_bin11  += rfv_tf_stats_err_vector[10] ;
  if (nHistbins>=12 )   rfv_bin12  += rfv_tf_stats_err_vector[11] ;
  */
  std::cout<<" stats error added "<<std::endl;

  // allow the stats error to vary fom 0 to  1* sigma
  // to make them gaussian constrained add param line in the datacards otherwise it is not gaussian constrained.
  RooRealVar rrv_stats_err_bin1("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin1", "rrv_stats_err_"+region_proc_cr+"_bin1",tf_stats_err_vector[0],  0.5*tf_stats_err_vector[0],2.*tf_stats_err_vector[0]);
  RooRealVar rrv_stats_err_bin2("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin2", "rrv_stats_err_"+region_proc_cr+"_bin2",tf_stats_err_vector[1],  0.5*tf_stats_err_vector[1],2.*tf_stats_err_vector[1]);
  RooRealVar rrv_stats_err_bin3("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin3", "rrv_stats_err_"+region_proc_cr+"_bin3",tf_stats_err_vector[2],  0.5*tf_stats_err_vector[2],2.*tf_stats_err_vector[2]);
  RooRealVar rrv_stats_err_bin4("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin4", "rrv_stats_err_"+region_proc_cr+"_bin4",tf_stats_err_vector[3],  0.5*tf_stats_err_vector[3],2.*tf_stats_err_vector[3]);

  // -- Following code is to extend the number of bins
  /*RooRealVar rrv_stats_err_bin5("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin5", "rrv_stats_err_"+region_proc_cr+"_bin5",tf_stats_err_vector[4],  0.5*tf_stats_err_vector[4],2.*tf_stats_err_vector[4]);
  RooRealVar rrv_stats_err_bin6("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin6", "rrv_stats_err_"+region_proc_cr+"_bin6",tf_stats_err_vector[5],  0.5*tf_stats_err_vector[5],2.*tf_stats_err_vector[5]);
  RooRealVar rrv_stats_err_bin7("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin7", "rrv_stats_err_"+region_proc_cr+"_bin7",tf_stats_err_vector[6],  0.5*tf_stats_err_vector[6],2.*tf_stats_err_vector[6]);
  RooRealVar rrv_stats_err_bin8("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin8", "rrv_stats_err_"+region_proc_cr+"_bin8",tf_stats_err_vector[7],  0.5*tf_stats_err_vector[7],2.*tf_stats_err_vector[7]);

  RooRealVar rrv_stats_err_bin9("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin9", "rrv_stats_err_"+region_proc_cr+"_bin9",tf_stats_err_vector[8],  0.5*tf_stats_err_vector[8],2.*tf_stats_err_vector[8]);
  RooRealVar rrv_stats_err_bin10("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin10", "rrv_stats_err_"+region_proc_cr+"_bin10",tf_stats_err_vector[9],  0.5*tf_stats_err_vector[9],2.*tf_stats_err_vector[9]);
  RooRealVar rrv_stats_err_bin11("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin11", "rrv_stats_err_"+region_proc_cr+"_bin11",tf_stats_err_vector[10],  0.5*tf_stats_err_vector[10],2.*tf_stats_err_vector[10]);
  RooRealVar rrv_stats_err_bin12("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin12", "rrv_stats_err_"+region_proc_cr+"_bin12",tf_stats_err_vector[11],  0.5*tf_stats_err_vector[11],2.*tf_stats_err_vector[11]);
  */

  RooArgList ral_bin1;
  RooArgList ral_bin2;
  RooArgList ral_bin3;
  RooArgList ral_bin4;

  /*
  RooArgList ral_bin5;
  RooArgList ral_bin6;
  RooArgList ral_bin7;
  RooArgList ral_bin8;

  RooArgList ral_bin9;
  RooArgList ral_bin10;
  RooArgList ral_bin11;
  RooArgList ral_bin12;
  */


  ral_bin1.add(tf1);
  ral_bin2.add(tf2);
  ral_bin3.add(tf3);
  ral_bin4.add(tf4);

  // Following code is to extend the number of bins
  /*if (nHistbins>=5 )  ral_bin5.add(tf5);
  if (nHistbins>=6 )  ral_bin6.add(tf6);
  if (nHistbins>=7 )  ral_bin7.add(tf7);
  if (nHistbins>=8 )  ral_bin8.add(tf8);

  if (nHistbins>=9 )  ral_bin9.add(tf9);
  if (nHistbins>=10 )  ral_bin10.add(tf10);
  if (nHistbins>=11 )  ral_bin11.add(tf11);
  if (nHistbins>=12 )  ral_bin12.add(tf12);
  */

  ral_bin1.add(rrv_stats_err_bin1);
  ral_bin2.add(rrv_stats_err_bin2);
  ral_bin3.add(rrv_stats_err_bin3);
  ral_bin4.add(rrv_stats_err_bin4);

  //  -- Following code is to extend the number of bins
  /*if (nHistbins>=5 ) ral_bin5.add(rrv_stats_err_bin5);
  if (nHistbins>=6 ) ral_bin6.add(rrv_stats_err_bin6);
  if (nHistbins>=7 ) ral_bin7.add(rrv_stats_err_bin7);
  if (nHistbins>=8 ) ral_bin8.add(rrv_stats_err_bin8);

  if (nHistbins>=9 ) ral_bin9.add(rrv_stats_err_bin9);
  if (nHistbins>=10 ) ral_bin10.add(rrv_stats_err_bin10);
  if (nHistbins>=11 ) ral_bin11.add(rrv_stats_err_bin11);
  if (nHistbins>=12 ) ral_bin12.add(rrv_stats_err_bin12);
  */

  RooRealVar* rrv_syst;
  //RooRealVar* rrv_syst_bin2;
  //RooRealVar* rrv_syst_bin3;
  //RooRealVar* rrv_syst_bin4;

  std::cout<<" number of nuisances : "<<nuisIndex.size()<<std::endl;

  for (int isys=0; isys < (int) nuisIndex.size(); isys++){
    std::vector<std::string> add_logN_systematic ;

    add_logN_systematic.clear();


    if (nuisIndex[isys]>23 ){
    add_logN_systematic = createnuisance(nuisanceValue[nuisIndex[isys]], nHistbins, syst_counter++);
  }

    /*if (nuisIndex[isys] != 8) add_logN_systematic = createnuisance(nuisanceValue[nuisIndex[isys]], nHistbins, syst_counter++);*/
    if (nuisIndex[isys] <=23 ) { // this will take value from the histogram NOT the flat value in vector.
      add_logN_systematic.clear();

      std::cout<<"------------------systematic name: "<<isys<<"  "<<nuisIndex[isys]<<" "<<anacat_orig+"/"+crname+"/"+nuisanceName[nuisIndex[isys]]<<std::endl;
      TH1F* btagunc = (TH1F*) fIn_->Get(anacat_orig+"/"+crname+"/"+nuisanceName[nuisIndex[isys]]);
      std::vector<float> btaguncvec = GetBinContents(btagunc);
      add_logN_systematic = createnuisance(btaguncvec, nHistbins, syst_counter++);
    }

    //for (int i =0; i<4; i++)  std::cout<<" add_logN_systematic = "<<add_logN_systematic[i]<<std::endl;
    rfv_bin1 += "*"+add_logN_systematic[0];
    rfv_bin2 += "*"+add_logN_systematic[1];
    rfv_bin3 += "*"+add_logN_systematic[2];
    rfv_bin4 += "*"+add_logN_systematic[3];

    // following code is to be exten
    /*if (nHistbins>=5 ) rfv_bin5 += "*"+add_logN_systematic[4];
    if (nHistbins>=6 ) rfv_bin6 += "*"+add_logN_systematic[5];
    if (nHistbins>=7 ) rfv_bin7 += "*"+add_logN_systematic[6];
    if (nHistbins>=8 ) rfv_bin8 += "*"+add_logN_systematic[7];

    if (nHistbins>=9 )  rfv_bin9  += "*"+add_logN_systematic[8];
    if (nHistbins>=10 ) rfv_bin10 += "*"+add_logN_systematic[9];
    if (nHistbins>=11 ) rfv_bin11 += "*"+add_logN_systematic[10];
    if (nHistbins>=12 ) rfv_bin12 += "*"+add_logN_systematic[11];
    */

    std::cout<<" bin 1 stats unc "<< rfv_bin1<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 2 stats unc "<< rfv_bin2<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 3 stats unc "<< rfv_bin3<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 4 stats unc "<< rfv_bin4<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;

    // following code is to be extend
    /*if (nHistbins>=5 ) std::cout<<" bin 5 stats unc "<< rfv_bin5<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    if (nHistbins>=6 ) std::cout<<" bin 6 stats unc "<< rfv_bin6<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    if (nHistbins>=7 ) std::cout<<" bin 7 stats unc "<< rfv_bin7<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    if (nHistbins>=8 ) std::cout<<" bin 8 stats unc "<< rfv_bin8<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    */

    //rrv_syst = new RooRealVar(nuisanceName[nuisIndex[isys]]+anacat_, "rrv_"+nuisanceName[nuisIndex[isys]], nuisanceValue[nuisIndex[isys]], 0., 1.*nuisanceValue[nuisIndex[isys]]);
    rrv_syst = new RooRealVar(nuisanceName[nuisIndex[isys]], "rrv_"+nuisanceName[nuisIndex[isys]], nuisanceValue[nuisIndex[isys]], 0., 1.*nuisanceValue[nuisIndex[isys]]);

    ral_bin1.add(*rrv_syst);
    ral_bin2.add(*rrv_syst);
    ral_bin3.add(*rrv_syst);
    ral_bin4.add(*rrv_syst); // it has to be pointer for some reason, otherwise it gives seg fault, not sure yet, why?

    //  -- Following code is to extend the number of bins
    /*if (nHistbins>=5 ) ral_bin5.add(*rrv_syst);
    if (nHistbins>=6 ) ral_bin6.add(*rrv_syst);
    if (nHistbins>=7 ) ral_bin7.add(*rrv_syst);
    if (nHistbins>=8 ) ral_bin8.add(*rrv_syst);

    if (nHistbins>=9 ) ral_bin9.add(*rrv_syst);
    if (nHistbins>=10 ) ral_bin10.add(*rrv_syst);
    if (nHistbins>=11 ) ral_bin11.add(*rrv_syst);
    if (nHistbins>=12 ) ral_bin12.add(*rrv_syst);
    */
  }

  std::cout<<" bins already included in the lists "<<ral_bin1<<std::endl;


  std::cout<<" bin 1 total unc is "<<rfv_bin1<<std::endl;
  std::cout<<" bin 2 total unc is "<<rfv_bin2<<std::endl;
  std::cout<<" bin 3 total unc is "<<rfv_bin3<<std::endl;
  std::cout<<" bin 4 total unc is "<<rfv_bin4<<std::endl;

  std::cout<<" RAL = "<<ral_bin1<<std::endl;
  RooFormulaVar TF1("TF1"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin1, ral_bin1);
  RooFormulaVar TF2("TF2"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin2, ral_bin2);
  RooFormulaVar TF3("TF3"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin3, ral_bin3);
  RooFormulaVar TF4("TF4"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin4, ral_bin4);

  //  -- Following code is to extend the number of bins
  /*RooFormulaVar TF5("TF5"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin5, ral_bin5);
  RooFormulaVar TF6("TF6"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin6, ral_bin6);
  RooFormulaVar TF7("TF7"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin7, ral_bin7);
  RooFormulaVar TF8("TF8"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin8, ral_bin8);

  RooFormulaVar TF9("TF9"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin9, ral_bin9);
  RooFormulaVar TF10("TF10"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin10, ral_bin10);
  RooFormulaVar TF11("TF11"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin11, ral_bin11);
  RooFormulaVar TF12("TF12"+region_proc_cr+anacat_+"_"+year_,"Transfer factor",rfv_bin12, ral_bin12);
  */

  /*
    Then need to make each bin of the background in the control region a function of the background in the signal and the transfer factor -
    i.e NCR=NSR x TF
  */
  std::cout<<" TF done "<<std::endl;


  //---- This is the usual formula to get the bkg in CR, from 8 Feb 2021 use the inverted implementation
  // RooFormulaVar rfv_cr_bkg1("rfv_"+region_proc_cr+"1"+anacat_+"_"+year_,"Background yield in control region, bin 1","@0*@1",RooArgList(TF1, rrvbc_sr_bkg.at(0)));
  // RooFormulaVar rfv_cr_bkg2("rfv_"+region_proc_cr+"2"+anacat_+"_"+year_,"Background yield in control region, bin 2","@0*@1",RooArgList(TF2,rrvbc_sr_bkg.at(1)));
  // RooFormulaVar rfv_cr_bkg3("rfv_"+region_proc_cr+"3"+anacat_+"_"+year_,"Background yield in control region, bin 3","@0*@1",RooArgList(TF3,rrvbc_sr_bkg.at(2)));
  // RooFormulaVar rfv_cr_bkg4("rfv_"+region_proc_cr+"4"+anacat_+"_"+year_,"Background yield in control region, bin 4","@0*@1",RooArgList(TF4,rrvbc_sr_bkg.at(3)));

  RooFormulaVar rfv_cr_bkg1("rfv_"+region_proc_cr+"1"+anacat_+"_"+year_,"Background yield in control region, bin 1","(1.0/@0)*@1",RooArgList(TF1, rrvbc_sr_bkg.at(0)));
  RooFormulaVar rfv_cr_bkg2("rfv_"+region_proc_cr+"2"+anacat_+"_"+year_,"Background yield in control region, bin 2","(1.0/@0)*@1",RooArgList(TF2,rrvbc_sr_bkg.at(1)));
  RooFormulaVar rfv_cr_bkg3("rfv_"+region_proc_cr+"3"+anacat_+"_"+year_,"Background yield in control region, bin 3","(1.0/@0)*@1",RooArgList(TF3,rrvbc_sr_bkg.at(2)));
  RooFormulaVar rfv_cr_bkg4("rfv_"+region_proc_cr+"4"+anacat_+"_"+year_,"Background yield in control region, bin 4","(1.0/@0)*@1",RooArgList(TF4,rrvbc_sr_bkg.at(3)));

  //  -- Following code is to extend the number of bins
  /*RooFormulaVar rfv_cr_bkg5("rfv_"+region_proc_cr+"5"+anacat_+"_"+year_,"Background yield in control region, bin 5","(1.0/@0)*@1",RooArgList(TF5,rrvbc_sr_bkg.at(4)));
  RooFormulaVar rfv_cr_bkg6("rfv_"+region_proc_cr+"6"+anacat_+"_"+year_,"Background yield in control region, bin 6","(1.0/@0)*@1",RooArgList(TF6,rrvbc_sr_bkg.at(5)));
  RooFormulaVar rfv_cr_bkg7("rfv_"+region_proc_cr+"7"+anacat_+"_"+year_,"Background yield in control region, bin 7","(1.0/@0)*@1",RooArgList(TF7,rrvbc_sr_bkg.at(6)));
  RooFormulaVar rfv_cr_bkg8("rfv_"+region_proc_cr+"8"+anacat_+"_"+year_,"Background yield in control region, bin 8","(1.0/@0)*@1",RooArgList(TF8,rrvbc_sr_bkg.at(7)));

  RooFormulaVar rfv_cr_bkg9("rfv_"+region_proc_cr+"9"+anacat_+"_"+year_,"Background yield in control region, bin 9","(1.0/@0)*@1",RooArgList(TF9,rrvbc_sr_bkg.at(8)));
  RooFormulaVar rfv_cr_bkg10("rfv_"+region_proc_cr+"10"+anacat_+"_"+year_,"Background yield in control region, bin 10","(1.0/@0)*@1",RooArgList(TF10,rrvbc_sr_bkg.at(9)));
  RooFormulaVar rfv_cr_bkg11("rfv_"+region_proc_cr+"11"+anacat_+"_"+year_,"Background yield in control region, bin 11","(1.0/@0)*@1",RooArgList(TF11,rrvbc_sr_bkg.at(10)));
  RooFormulaVar rfv_cr_bkg12("rfv_"+region_proc_cr+"12"+anacat_+"_"+year_,"Background yield in control region, bin 12","(1.0/@0)*@1",RooArgList(TF12,rrvbc_sr_bkg.at(11)));
  */


  // --------------------------------------------------------------
  // ------------------------WJets (muon ) Control region ---------
  // --------------------------------------------------------------

  RooArgList ral_cr_bkg;
  ral_cr_bkg.add(rfv_cr_bkg1);
  ral_cr_bkg.add(rfv_cr_bkg2);
  ral_cr_bkg.add(rfv_cr_bkg3);
  ral_cr_bkg.add(rfv_cr_bkg4);

  //  -- Following code is to extend the number of bins
  /*if (nHistbins>=5 ) ral_cr_bkg.add(rfv_cr_bkg5);
  if (nHistbins>=6 ) ral_cr_bkg.add(rfv_cr_bkg6);
  if (nHistbins>=7 ) ral_cr_bkg.add(rfv_cr_bkg7);
  if (nHistbins>=8 ) ral_cr_bkg.add(rfv_cr_bkg8);

  if (nHistbins>=9 ) ral_cr_bkg.add(rfv_cr_bkg9);
  if (nHistbins>=10 ) ral_cr_bkg.add(rfv_cr_bkg10);
  if (nHistbins>=11 ) ral_cr_bkg.add(rfv_cr_bkg11);
  if (nHistbins>=12 ) ral_cr_bkg.add(rfv_cr_bkg12);
  */

  RooParametricHist rph_cr_bkg("rph_"+region_proc_cr+anacat_+"_"+year_, "Background PDF in control region",met,ral_cr_bkg, *h_sr_data);
  RooAddition rph_cr_bkg_norm("rph_"+region_proc_cr+anacat_+"_"+year_+"_norm","Total Number of events from background in control region", ral_cr_bkg);

  wspace.import(rph_cr_bkg);
  wspace.import(rph_cr_bkg_norm ,RooFit::RecycleConflictNodes());

  std::cout<<" workspace for one CR is imported. "<<std::endl;



}




void PrepareWS_withnuisanceInvertTF_noW_nBins(TString model_="monoHbb",TString analysiscategory_="merged", TString mode__ = "RECREATE", TString inputdir=".", TString inputfile="AllMETHistos.root", TString year="2016", int nbins=4,TString version     = "_V0"){


  TString anacat_ = analysiscategory_;

  TString outputfile  = model_+"_"+year+"_WS.root";
  TString cat__ =  analysiscategory_;


  bool debug__ = true;

  TString AnaYearCat  = model_ +  year + "_" + cat__ +"_" ;
  std::cout<<" AnaYearCat = "<<AnaYearCat<<std::endl;
  bool usebkgsum = false;


  // Get the binning from histogram which can be used later in the code throughout.
  // Open input file with all the histograms.
  TFile* fin = OpenRootFile(inputdir+"/"+inputfile);

  TH1F* h_binning = (TH1F*) fin->Get("bbDM"+year+"_"+anacat_+"_SR_2HDMa_Ma500_MChi1_MA600_tb35_st_0p7");


  Double_t bins[nbins+1];
  int  met_low = h_binning->GetBinLowEdge(1);
  int  met_hi  = h_binning->GetBinLowEdge(nbins+1);

  std::cout<< "met_low: met_hi: "<<met_low<<" "<<met_hi<<std::endl;

  for (int ibin=1; ibin<=nbins+1;ibin++){
    bins[ibin-1] = h_binning->GetBinLowEdge(ibin);
    //std::cout<<" bins = "<<ibin<<" "<<bins[ibin-1]<<std::endl;
  }
  std::cout<<" integral of the histogram is"<<h_binning->Integral()<<std::endl;

  for (int ibin=0; ibin<=nbins;ibin++){
    std::cout<<" bins = "<<ibin<<" "<<bins[ibin]<<std::endl;
  }

  //int met_low = 250;
  //int met_hi = 1000;
  //int met_low = -1;
  //int met_hi = 1;

  h_vec_tf.clear();

  // Double_t bins[]={200, 250, 350, 500, 1000};
  //Double_t bins[]={250.,300.,400.,550., 1000.};  // baseline
  //Double_t bins[]={250,275,300,350,400,475,550,775,1000};



  // Double_t bins[]={250., 280., 340., 460., 1000.}; // to get more stat in last bin
  // Double_t bins[] = {-1, -0.1, 0.0, 0.1, 1.0};  // binset4

  //Double_t bins[] = {-1, -0.1, -0.03,0.03, 0.1, 1.0}; //binset7

  //Double_t bins[]={250.,300.,350,400.,500.};
  //Double_t bins[]={250.,313.,375.,437.,500.};

  Int_t  binnum = sizeof(bins)/sizeof(Double_t) - 1;

  // As usual, load the combine library to get access to the RooParametricHist
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  // Output file and workspace
  TFile* fOut = OpenRootFile(outputfile,mode__);

  TString workspacename = "ws_"+model_+"_"+analysiscategory_+"_"+year;
  TString workspacetitle = "work space for year "+year+", analysis "+model_+", category "+analysiscategory_;
  RooWorkspace wspace(workspacename,workspacetitle);

  TString fitvariable_ = "";
  if (anacat_=="1b") fitvariable_="met";
  if (anacat_=="2b") fitvariable_="cts";

  // A search in a MET tail, define MET as our variable
  RooRealVar met(fitvariable_, fitvariable_ ,met_low, met_hi);
  RooArgList vars(met);

  std::cout<<" debug 2" <<std::endl;






  // this histogram is just for the binning
  // --- commented on 5 Feb to see if the limis becomes same when using the opriginal data histogram


  TH1F* h_sr_data = (TH1F*) fin->Get(AnaYearCat+"SR_bkgSum");

  std::cout<< "histogram name binning: "<<h_sr_data->GetName()<<" "<<AnaYearCat+"SR_bkgSum"<<std::endl;
  //the following lines create a freely floating parameter for each of our bins (in this example, there are only 4 bins, defined for our observable met.
  // In this case we vary the normalisation in each bin of the background from N/3 to 3*N,
  // e.g. if actual content in the histogram is 55 then we initialize
  // it with 55 and vary it from 55/3 to 55*3. which is very close to freely floating. This can be checked if this works for the cases when bin content is very low,
  // specially in the tails and can be changed easily .



  std::vector <TString> nuisanceName;
  std::vector <float> nuisanceValue;

  nuisanceName.clear();    nuisanceValue.clear();
  TString nuisancePostfix = "CMS"+year+"_";
  nuisanceValue.clear();


  nuisanceName.push_back(nuisancePostfix+"trig_ele");             nuisanceValue.push_back(0.02) ;  //  0
  nuisanceName.push_back(nuisancePostfix+"EleRECO");              nuisanceValue.push_back(0.01) ;  //  1
  nuisanceName.push_back(nuisancePostfix+"EleID");                nuisanceValue.push_back(0.07) ;  //  2

  nuisanceName.push_back(nuisancePostfix+"MuTRK");                nuisanceValue.push_back(0.03) ;   // 3
  nuisanceName.push_back(nuisancePostfix+"MuID");                 nuisanceValue.push_back(0.01) ;   // 4
  nuisanceName.push_back(nuisancePostfix+"MuISO");                nuisanceValue.push_back(0.01) ;   // 5

  nuisanceName.push_back(nuisancePostfix+"metTrig");              nuisanceValue.push_back(0.01) ;   // 6
  nuisanceName.push_back(nuisancePostfix+"prefire");              nuisanceValue.push_back(0.01) ;   // 7
  nuisanceName.push_back(nuisancePostfix+"eff_b");                nuisanceValue.push_back(0.10) ;   // 8

  nuisanceName.push_back("JECAbsolute");          nuisanceValue.push_back(0.01); // 9
  nuisanceName.push_back("JECFlavorQCD");         nuisanceValue.push_back(0.01); // 10
  nuisanceName.push_back("JECBBEC1");             nuisanceValue.push_back(0.01); // 11
  nuisanceName.push_back("JECRelativeBal");   nuisanceValue.push_back(0.01); // 12

  nuisanceName.push_back("JECAbsolute_"+year);   nuisanceValue.push_back(0.01); // 13
  nuisanceName.push_back("JECRelativeSample_"+year);   nuisanceValue.push_back(0.01); // 14

  nuisanceName.push_back(nuisancePostfix+"pdf"); nuisanceValue.push_back(0.10); // 15
  nuisanceName.push_back(nuisancePostfix+"mu_scale_zjets"); nuisanceValue.push_back(0.10); // 16
  nuisanceName.push_back(nuisancePostfix+"mu_scale_wjets"); nuisanceValue.push_back(0.10); // 17
  nuisanceName.push_back(nuisancePostfix+"mu_scale_tt"); nuisanceValue.push_back(0.10); // 18
  nuisanceName.push_back(nuisancePostfix+"mu_scale_singlet"); nuisanceValue.push_back(0.10);  // 19
  nuisanceName.push_back(nuisancePostfix+"mu_scale_qcd"); nuisanceValue.push_back(0.10);  // 20
  nuisanceName.push_back(nuisancePostfix+"mu_scale_dyjets"); nuisanceValue.push_back(0.10); // 21
  nuisanceName.push_back(nuisancePostfix+"mu_scale_diboson"); nuisanceValue.push_back(0.10);  // 22
  nuisanceName.push_back(nuisancePostfix+"mu_scale_smh"); nuisanceValue.push_back(0.10);  // 23


  /*nuisanceName.push_back(nuisancePostfix+"");   nuisanceValue.push_back(0.01); // 15
  nuisanceName.push_back(nuisancePostfix+"");   nuisanceValue.push_back(0.01); // 16
  */

  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top mu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  std::vector<int> nuisIndex; nuisIndex.clear(); // this is the index of nuisances which are to be used for mu CR

  if(anacat_=="2b"){

  std::cout<<" calling function for Top mu: "<<AnaYearCat+"SR_tt"<<std::endl;
  TH1F* h_sr_top = (TH1F*) fin->Get(AnaYearCat+"SR_tt");
  // Get the top hostogram in the Top mu CR
  TH1F* h_topmu_2b_top = (TH1F*) fin->Get(AnaYearCat+"TOPMU_tt");


  // Create all the inputs needed for this CR
  // list of systematics for Top mu CR
  if (year=="2016"){
    nuisIndex.push_back(3);
    nuisIndex.push_back(7);
  }

  nuisIndex.push_back(4);
  nuisIndex.push_back(5);

  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  //nuisIndex.push_back(15);
  //nuisIndex.push_back(16);


  if (year=="2017"){
    nuisIndex.push_back(7);
  }


  // mu efficiency for Top mu CR
  createRegion(met, h_sr_top, h_topmu_2b_top, h_sr_data, wspace, "TOPMU_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_,year,fin,"TOPMU");


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top e CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


  nuisIndex.clear();
  nuisIndex.push_back(0);
  nuisIndex.push_back(1);
  nuisIndex.push_back(2);

  //nuisIndex.push_back(6);
  if (year=="2017") nuisIndex.push_back(7);

  if (year=="2016"){
    nuisIndex.push_back(7);
  }

  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  //nuisIndex.push_back(15);
  //nuisIndex.push_back(16);


    std::cout<<" calling function for Top e"<<std::endl;
  // Get the top hostogram in the Top mu CR
  TH1F* h_tope_2b_top = (TH1F*) fin->Get(AnaYearCat+"TOPE_tt");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr_top, h_tope_2b_top, h_sr_data, wspace, "TOPE_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue,anacat_,year,fin,"TOPE");
  }/// if(anacat_=="2b")

  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W enu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
   */


  std::cout<<" anacat_: "<<(anacat_=="1b")<<std::endl;
  nuisIndex.clear();
  if (anacat_=="1b"){

  nuisIndex.push_back(0);
  nuisIndex.push_back(1);
  nuisIndex.push_back(2);
  //nuisIndex.push_back(6);

  if (year=="2016"){
    nuisIndex.push_back(7);
  }

  if (year=="2017") nuisIndex.push_back(7);

  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  //nuisIndex.push_back(15);
  //nuisIndex.push_back(16);


  std::cout<<" calling function for Wenu"<<nuisIndex.size()<<std::endl;
  for (int i=0; i<(int) nuisIndex.size();i++) std::cout<< "nuisIndex : "<<nuisIndex[i]<<std::endl;
  // Get the wjets histogram in signal region
  TH1F* h_sr_wjets = (TH1F*) fin->Get(AnaYearCat+"SR_wjets");

  // Get the wjets hostogram in the Wenu CR
  TH1F* h_wenu_2b_wjets = (TH1F*) fin->Get(AnaYearCat+"WE_wjets");

  std::cout<<" integral of wenu : "<<h_sr_wjets->Integral() <<"  "<<h_wenu_2b_wjets->Integral()<<std::endl;
  // Create all the inputs needed for this CR
  createRegion(met, h_sr_wjets, h_wenu_2b_wjets, h_sr_data, wspace, "WE_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WE");

  //  fixme, creating new for cross-transfer factors
  // ttbar in SR linked to top in W+Jets
  //TH1F* h_wenu_2b_top = (TH1F*) fin->Get(AnaYearCat+"WE_tt");
  //createRegion(met, h_sr_top, h_wenu_2b_top, h_sr_data, wspace, "WE_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WE");


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W munu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
    */


  nuisIndex.clear();
  if (year=="2016"){
    nuisIndex.push_back(3);
    nuisIndex.push_back(7);
  }
  nuisIndex.push_back(4);
  nuisIndex.push_back(5);
  if (year=="2017") nuisIndex.push_back(7);

  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  //nuisIndex.push_back(15);
  //nuisIndex.push_back(16);



  //TH1F* h_sr_wjets = (TH1F*) fin->Get(AnaYearCat+"SR_wjets");

  std::cout<<" calling function for Wmunu"<<std::endl;
  // Get the wjets hostogram in the Wmunu CR
  TH1F* h_wmunu_2b_wjets = (TH1F*) fin->Get(AnaYearCat+"WMU_wjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr_wjets, h_wmunu_2b_wjets, h_sr_data, wspace, "WMU_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WMU");

  //  fixme, creating new for cross-transfer factors
  // ttbar in SR linked to top in W+Jets
  //TH1F* h_wmunu_2b_top = (TH1F*) fin->Get(AnaYearCat+"WMU_tt");
  //createRegion(met, h_sr_top, h_wmunu_2b_top, h_sr_data, wspace, "WMU_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,WMU);

  }
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zmumu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  nuisIndex.clear();
  if (year=="2016"){
    nuisIndex.push_back(3);
    nuisIndex.push_back(7);
  }
  nuisIndex.push_back(4);
  nuisIndex.push_back(5);
  if (year=="2017") nuisIndex.push_back(7);
  nuisIndex.push_back(8);

  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  nuisIndex.push_back(15);
  nuisIndex.push_back(16);



  std::cout<<" calling function for Zmumu"<<std::endl;
  TH1F* h_sr_Z = (TH1F*) fin->Get(AnaYearCat+"SR_zjets");
  // Get the top hostogram in the Top mu CR
  TH1F* h_Zmumu_2b_Z = (TH1F*) fin->Get(AnaYearCat+"ZMUMU_dyjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr_Z, h_Zmumu_2b_Z, h_sr_data, wspace, "ZMUMU_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"ZMUMU");


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zee CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  nuisIndex.clear();
  nuisIndex.push_back(0);
  nuisIndex.push_back(1);
  nuisIndex.push_back(2);
  //nuisIndex.push_back(6);
  if (year=="2016"){
    nuisIndex.push_back(7);
  }
  if (year=="2017") {
    nuisIndex.push_back(7);
  }

  nuisIndex.push_back(8);


  //JECs  9-14
  nuisIndex.push_back(9);
  nuisIndex.push_back(10);
  nuisIndex.push_back(11);
  nuisIndex.push_back(12);
  nuisIndex.push_back(13);
  nuisIndex.push_back(14);
  nuisIndex.push_back(15);
  nuisIndex.push_back(16);



  // Get the top hostogram in the Top mu CR
  TH1F* h_Zee_2b_Z = (TH1F*) fin->Get(AnaYearCat+"ZEE_dyjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr_Z, h_Zee_2b_Z, h_sr_data, wspace, "ZEE_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"ZEE");

  std::cout<<" all crs done "<<std::endl;


  //} // end of the debug__
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Signal -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  std::vector<TString> nuisancesName;
  nuisancesName.clear();
  nuisancesName.push_back("");
  // ups
  nuisancesName.push_back("CMS"+year+"_PUUp");
  nuisancesName.push_back("CMS"+year+"_eff_bUp");
  nuisancesName.push_back("CMS"+year+"_fake_bUp");
  nuisancesName.push_back("CMS"+year+"_trig_metUp");
  nuisancesName.push_back("CMS"+year+"_trig_eleUp");
  nuisancesName.push_back("CMS"+year+"_EleIDUp");
  nuisancesName.push_back("CMS"+year+"_EleRECOUp");
  nuisancesName.push_back("CMS"+year+"_MuTRKUp");
  nuisancesName.push_back("CMS"+year+"_MuIDUp");
  nuisancesName.push_back("CMS"+year+"_MuISOUp");
  nuisancesName.push_back("CMS"+year+"_pdfUp");

  nuisancesName.push_back("CMS"+year+"_mu_scale_signalUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_zjetsUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_wjetsUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_ttUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_singletUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_qcdUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_dibosonUp");
  nuisancesName.push_back("CMS"+year+"_mu_scale_smhUp");


  nuisancesName.push_back("JECAbsoluteUp");
  nuisancesName.push_back("JECAbsolute_"+year+"Up");
  nuisancesName.push_back("JECBBEC1Up");
  nuisancesName.push_back("JECBBEC1_"+year+"Up");
  nuisancesName.push_back("JECEC2Up");
  nuisancesName.push_back("JECEC2_"+year+"Up");
  nuisancesName.push_back("JECFlavorQCDUp");
  nuisancesName.push_back("JECHFUp");
  nuisancesName.push_back("JECHF_"+year+"Up");
  nuisancesName.push_back("JECRelativeBalUp");
  nuisancesName.push_back("JECRelativeSample_"+year+"Up");


  nuisancesName.push_back("CMS"+year+"_prefireUp");


  // down
  nuisancesName.push_back("CMS"+year+"_PUDown");
  nuisancesName.push_back("CMS"+year+"_eff_bDown");
  nuisancesName.push_back("CMS"+year+"_fake_bDown");
  nuisancesName.push_back("CMS"+year+"_trig_metDown");
  nuisancesName.push_back("CMS"+year+"_trig_eleDown");
  nuisancesName.push_back("CMS"+year+"_EleIDDown");
  nuisancesName.push_back("CMS"+year+"_EleRECODown");
  nuisancesName.push_back("CMS"+year+"_MuTRKDown");
  nuisancesName.push_back("CMS"+year+"_MuIDDown");
  nuisancesName.push_back("CMS"+year+"_MuISODown");
  nuisancesName.push_back("CMS"+year+"_pdfDown");


  nuisancesName.push_back("CMS"+year+"_mu_scale_signalDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_zjetsDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_wjetsDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_ttDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_singletDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_qcdDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_dibosonDown");
  nuisancesName.push_back("CMS"+year+"_mu_scale_smhDown");


  nuisancesName.push_back("JECAbsoluteDown");
  nuisancesName.push_back("JECAbsolute_"+year+"Down");
  nuisancesName.push_back("JECBBEC1Down");
  nuisancesName.push_back("JECBBEC1_"+year+"Down");
  nuisancesName.push_back("JECEC2Down");
  nuisancesName.push_back("JECEC2_"+year+"Down");
  nuisancesName.push_back("JECFlavorQCDDown");
  nuisancesName.push_back("JECHFDown");
  nuisancesName.push_back("JECHF_"+year+"Down");
  nuisancesName.push_back("JECRelativeBalDown");
  nuisancesName.push_back("JECRelativeSample_"+year+"Down");

  nuisancesName.push_back("CMS"+year+"_prefireDown");

  // stats  only for signal for now
  nuisancesName.push_back("stat_bin1Up");
  nuisancesName.push_back("stat_bin2Up");
  nuisancesName.push_back("stat_bin3Up");
  nuisancesName.push_back("stat_bin4Up");

  nuisancesName.push_back("stat_bin1Down");
  nuisancesName.push_back("stat_bin2Down");
  nuisancesName.push_back("stat_bin3Down");
  nuisancesName.push_back("stat_bin4Down");


  //-------------------------------------------------//
  // --------- ADD 2HDM+a signal shapes -------------//
  //-------------------------------------------------//
  std::vector<int> signalpoint;
  signalpoint.clear();
  if (year!="2016"){
    //signalpoint.push_back(10);
    signalpoint.push_back(450);
  }

  if (year=="2017" || year == "2018" || year == "2016") {
    signalpoint.push_back(10);
    signalpoint.push_back(50);
    signalpoint.push_back(100);
    signalpoint.push_back(150);
    signalpoint.push_back(200);
    signalpoint.push_back(250);
    signalpoint.push_back(300);
    signalpoint.push_back(350);
    signalpoint.push_back(400);
    signalpoint.push_back(500);

  }

  std::vector<int> mApoint;
  mApoint.clear();
  mApoint.push_back(600.);
  //mApoint.push_back(1200.);


  Int_t  nsig = signalpoint.size();

  TString mps;
  TString mAs;
  for (auto inuis=0; inuis<nuisancesName.size(); inuis++){
    for (auto is=0; is<nsig; is++){

    for (auto imA=0; imA<mApoint.size(); imA++){
      mAs.Form("%d",mApoint[imA]);
      mps.Form("%d",signalpoint[is]);
      if (year=="2016"){
	if (mApoint[imA] == 1200 ) continue;
	if ( (signalpoint[is] == 100) && (mApoint[imA] == 1200) ) continue;
	if ( (signalpoint[is] == 300) && (mApoint[imA] == 1200) ) continue;
      }

      TString signalname = AnaYearCat+"SR_2HDMa_Ma"+mps+"_MChi1_MA"+mAs+"_tb35_st_0p7";
      if (nuisancesName[inuis]!="") signalname = signalname  + "_" +nuisancesName[inuis];
      if ((TH1F*) fin->Get(signalname) == 0 ) {
	std::cout<<" histogram : "<<  signalname <<" does not exist"<<std::endl;
      }

      if ((TH1F*) fin->Get(signalname) != 0 )  {
	std::cout<<" histogram : "<<  signalname <<" exist and saving "<<std::endl;
	addTemplate(wspace, vars, (TH1F*) fin->Get(signalname)  );
      }
      std::cout<<" ........ saved"<<std::endl;

    }
  }
  }


  //-------------------------------------------------//
  // --------- ADD DMSIMP signal shapes -------------//
  //-------------------------------------------------//
  std::vector<int> mphi, mChi;
  mphi.clear(); mChi.clear();

  mphi.push_back(10);
  mphi.push_back(50);
  mphi.push_back(100);
  mphi.push_back(150);
  mphi.push_back(200);
  mphi.push_back(250);
  mphi.push_back(300);
  mphi.push_back(400);
  mphi.push_back(450);
  mphi.push_back(500);
  mphi.push_back(700);
  mphi.push_back(750);
  mphi.push_back(1000);

  mChi.push_back(1);

  TString MPHI;
  TString MCHI;
  for (auto inuis=0; inuis<nuisancesName.size(); inuis++){
    for (auto iphi=0; iphi<int(mphi.size()); iphi++){

      for (auto iChi=0; iChi<mChi.size(); iChi++){
	MPHI.Form("%d",mphi[iphi]);
	MCHI.Form("%d",mChi[iChi]);

	TString signalname = AnaYearCat+"SR_DMSimp_MPhi"+MPHI+"_MChi"+MCHI;
	if (nuisancesName[inuis]!="") signalname = signalname  + "_" +nuisancesName[inuis];
	if ((TH1F*) fin->Get(signalname) == 0 ) {
	  std::cout<<" histogram : "<<  signalname <<" does not exist"<<std::endl;
	}

	if ((TH1F*) fin->Get(signalname) != 0 )  {
	  std::cout<<" histogram : "<<  signalname <<" exist and saving "<<std::endl;
	  addTemplate(wspace, vars, (TH1F*) fin->Get(signalname)  );
	}
	std::cout<<" ........ saved"<<std::endl;

      }
    }
  }



  if (!usebkgsum){
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"SR_data_obs" ) );
    //addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"SR_bkgSum") , AnaYearCat+"SR_data_obs" );
    if (anacat_=="2b"){
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPE_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPMU_data_obs" ) );
    }
    if (anacat_=="1b"){
      addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WE_data_obs" ) );
      addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WMU_data_obs" ) );
    }
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"ZEE_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"ZMUMU_data_obs" ) );

  }
  if (usebkgsum){

    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"SR_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPE_bkgSum" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPMU_bkgSum" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WE_bkgSum" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WMU_bkgSum" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"ZEE_bkgSum" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"ZMUMU_bkgSum" ) );
  }


 // all other histograms
  std::vector<TString> regions;
  regions.push_back("SR");
  regions.push_back("TOPE");
  regions.push_back("TOPMU");
  regions.push_back("WE");
  regions.push_back("WMU");
  regions.push_back("ZEE");
  regions.push_back("ZMUMU");


  std::vector<TString> process;

  process.push_back("diboson");
  process.push_back("gjets");
  process.push_back("qcd");
  process.push_back("zjets");
  process.push_back("smh");
  process.push_back("wjets");
  process.push_back("dyjets");
  process.push_back("tt");
  process.push_back("singlet");


  std::vector<TString> category;
  category.push_back(AnaYearCat);

  TString tempname;
  TString outhistnamestat;
  outhistnamestat="";
  for (auto inuis=0; inuis<nuisancesName.size(); inuis++){
    for (auto ir=0; ir<regions.size(); ir++){

      for (auto ip=0; ip<process.size(); ip++){

	for (auto ic=0; ic<category.size(); ic++){
	  //if (process[ip] == "wjets" && ( (regions[ir] =="WE") || (regions[ir] =="WMU") ) ) continue ;
	  //if (process[ip] == "tt" && ( (regions[ir] =="TOPE") || (regions[ir] =="TOPMU") ) ) continue ;


	  tempname = category[ic] + regions[ir] + "_" +  process[ip] ;

	  //outhistnamestat=tempname;
	  //if (nuisancesName[inuis].Contains("stat_")){
	  //  outhistnamestat = category[ic] + regions[ir] + "_" +  process[ip] + "_" + regions[ir] + "_" +  process[ip];
	  // }

	  if (nuisancesName[inuis]!="") {
	    tempname = tempname  + "_" +nuisancesName[inuis];

	    outhistnamestat=tempname;
	    if (nuisancesName[inuis].Contains("stat_")){
	      outhistnamestat.ReplaceAll(nuisancesName[inuis], "CMS"+year+"_"+anacat_+"_"+regions[ir] + "_" +  process[ip] + "_" + nuisancesName[inuis]);
	    }
	  }
	  if ((TH1F*) fin->Get(tempname) == 0 ) {
	    std::cout<<" histogram : "<< 	tempname <<" does not exist"<<std::endl;
	  }

	  if ((TH1F*) fin->Get(tempname) != 0 )  {
	    std::cout<<" histogram : "<<  tempname <<" exist and saving "<<outhistnamestat<<std::endl;
	    addTemplate(wspace, vars, (TH1F*) fin->Get(tempname)  ,outhistnamestat);
	  }
	  std::cout<<" ........ saved"<<std::endl;

	}
      }
    }
  }


  // write the workspace at the very end, once everthing has been imported to the workspace
  fOut->cd();
  wspace.Write();
  TString dirname_ = "transferfactor_" + model_ +"_"  +year + "_" + cat__  ;
  fOut->mkdir(dirname_);
  fOut->cd(dirname_);
  for (int i=0; i< (int) h_vec_tf.size(); i++) h_vec_tf[i]->Write();

}
