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

using namespace RooFit ;

/*
.C  Package to build statistical fitting model for background estimation and limit extraction
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

RooArgList: ral_wenu_wjets
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

  int nbinsx = h->GetNbinsX();
  for (auto ibin=1; ibin<=nbinsx; ibin++){
    bcs.push_back(h->GetBinContent(ibin));
  }

  return bcs;

}




void addTemplate(RooWorkspace& ws,  RooArgList& vars, TH1F* hist) {
  std::cout<<" name = "<<hist->GetName()<<std::endl;
  RooDataHist rhist(hist->GetName(), hist->GetName(),  vars, hist);
  std::cout<<" integral of the histogram for "<<hist->GetName()<<" is "<<rhist.sumEntries()<<"  "<<hist->Integral()<<std::endl;
  ws.import(rhist);
}


// This function is overloaded
std::vector <RooRealVar> GetRooRealVar(std::vector<float>  bcs, TString name){
  std::vector<RooRealVar> rrvV_ ;
  rrvV_.clear();
  TString postfix;

  for (auto i=0; i<bcs.size(); i++){
    postfix.Form("%d", i+1);
    // fix the naming here using some automation  and also in the next function

    std::cout<<" name inside GetRooRealVar = "<<name+postfix<<std::endl;
    rrvV_.push_back(RooRealVar(name+postfix,"Background yield in signal region, bin 1", bcs[i], 0,10*bcs[i]));

  }

  return rrvV_;
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
*/
void createRegion(RooRealVar met, TH1F* h_sr2_wjets , TH1F* h_wenu_2b_wjets, TH1F* h_sr2_data, RooWorkspace& wspace, TString region_proc_cr, TString region_proc_sr, TFile* fOut){

  RooArgList vars(met);

  /* Get the bin content of each bin of the histogram in a vector which can be used later */
  std::vector<float> bincontents_sr2_wjets = GetBinContents(h_sr2_wjets);

  // This will create the RooRealVar with 0 to 10*bin content  range.
  // create a vector of RooRealVar, this is needed because I didn't find  way to retrive the RooRealVar back from the RooArgList
  std::vector<RooRealVar> rrvbc_sr2_wjets = GetRooRealVar(bincontents_sr2_wjets, "rrvbc_"+region_proc_sr);

  RooArgList ralbc_sr2_wjets;
  ralbc_sr2_wjets.add(rrvbc_sr2_wjets[0]);
  ralbc_sr2_wjets.add(rrvbc_sr2_wjets[1]);
  ralbc_sr2_wjets.add(rrvbc_sr2_wjets[2]);
  ralbc_sr2_wjets.add(rrvbc_sr2_wjets[3]);

  // Create a RooParametericHist which contains those yields, last argument is just for the binning, we can use the data TH1 for that
  RooParametricHist rph_sr2_wjets("rph_"+region_proc_sr, "wjets PDF in signal region",met,ralbc_sr2_wjets, *h_sr2_data);

  // Always include a _norm term which should be the sum of the yields (thats how combine likes to play with pdfs)
  RooAddition rph_sr2_wjets_norm("rph_"+region_proc_sr+"_norm","Total Number of events from background in signal region",ralbc_sr2_wjets);


  wspace.import(rph_sr2_wjets);
  wspace.import(rph_sr2_wjets_norm,RooFit::RecycleConflictNodes());


  /*
    For the control region, the background process will be dependent on the yields of the background in the signal region using a transfer factor.
    The transfer factor TF must account for acceptance/efficiency etc differences in the signal to control regions.
    In this case we define the transfer factor as: ratio of the WJets (electron) yield in the WJets control region and
    WJets in the Signal region.

    For each bin a transfer factor is calculated and the nuisance parameters are associated with this.

    We could imagine that the transfer factor could be associated with some uncertainty - lets say a 1% uncertainty due to efficiency and 2% due to acceptance.
    We need to make nuisance parameters ourselves to model this and give them a nominal value of 0.
  */

  RooRealVar efficiency("efficiency", "efficiency nuisance parameter",0);
  RooRealVar acceptance("acceptance", "acceptance nuisance parameter",0);


  /*
  We need to make the transfer factor a function of these parameters since variations in these uncertainties will lead to variations of the transfer factor. Here we've assumed Log-normal effects (i.e the same as putting lnN in the CR datacard) but we could use any function which could be used to parameterise the effect - eg if the systematic is due to some alternate template, we could use polynomials for example.
  */


  // --------------------------------------------------------------
  // ------------------------Wjets (electrron) Control region ------
  // --------------------------------------------------------------

  // create roodatahist of the background histogram in CR.
  RooDataHist dh_wenu_2b_wjets("dh_"+region_proc_cr,"dh_"+region_proc_cr, vars, h_wenu_2b_wjets);

  // another copy fo the wjets in wenu CR for division and saving thr TFs central value.
  TH1F* htf_wenu_2b_wjets = (TH1F*) h_wenu_2b_wjets->Clone();
  htf_wenu_2b_wjets->Divide(h_sr2_wjets);


  std::cout<<" ratio "<< htf_wenu_2b_wjets->GetBinContent(1)
	   <<" "<<htf_wenu_2b_wjets->GetBinContent(2)
	   <<" "<<htf_wenu_2b_wjets->GetBinContent(3)
	   <<" "<<htf_wenu_2b_wjets->GetBinContent(4)
	   <<std::endl
	   <<"  SR yield =" <<h_sr2_wjets->GetBinContent(1)
	   <<" "<<h_sr2_wjets->GetBinContent(2)
	   <<" "<<h_sr2_wjets->GetBinContent(3)
	   <<" "<<h_sr2_wjets->GetBinContent(4)
	   <<std::endl
	   <<" "<<h_wenu_2b_wjets->GetBinContent(1)
	   <<" "<<h_wenu_2b_wjets->GetBinContent(2)
	   <<" "<<h_wenu_2b_wjets->GetBinContent(3)
	   <<" "<<h_wenu_2b_wjets->GetBinContent(4)
	   <<std::endl   ;


  // Get bin content of each bin of this ratio histogram and save it in the RooRealVar which will be used later for the Actual Transfer Factor with effect of Nuisance parameters included
  // idelaly each of these rooreal var in following vector should be setConstat(1) otherwise it may be treated as free parameter however it should be fixed.
  std::vector <float> bincontents_htf_wenu_2b_wjets =  GetBinContents(htf_wenu_2b_wjets);

  RooRealVar tf1 ("tf1_"+region_proc_cr,"tf1_"+region_proc_cr,bincontents_htf_wenu_2b_wjets[0]) ;
  RooRealVar tf2 ("tf2_"+region_proc_cr,"tf2_"+region_proc_cr,bincontents_htf_wenu_2b_wjets[1]) ;
  RooRealVar tf3 ("tf3_"+region_proc_cr,"tf3_"+region_proc_cr,bincontents_htf_wenu_2b_wjets[2]) ;
  RooRealVar tf4 ("tf4_"+region_proc_cr,"tf4_"+region_proc_cr,bincontents_htf_wenu_2b_wjets[3]) ;

  // the nuisance part of the code has to be updated after some more discussion.
  std::vector<RooRealVar> nuisances;
  nuisances.clear();
  nuisances.push_back(efficiency);
  nuisances.push_back(acceptance);


  RooFormulaVar TF1("TF1"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf1));//rrv_htf_wenu_2b_wjets[0]) );
  RooFormulaVar TF2("TF2"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf2));//rrv_htf_wenu_2b_wjets[1]) );
  RooFormulaVar TF3("TF3"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf3));//rrv_htf_wenu_2b_wjets[2]) );
  RooFormulaVar TF4("TF4"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf4));//rrv_htf_wenu_2b_wjets[3]) );

  /*
    Then need to make each bin of the background in the control region a function of the background in the signal and the transfer factor -
    i.e NCR=NSR x TF
  */




  RooFormulaVar rfv_wenu_2b_wjets1("rfv_"+region_proc_cr+"1","Background yield in control region, bin 1","@0*@1",RooArgList(TF1, rrvbc_sr2_wjets.at(0)));
  RooFormulaVar rfv_wenu_2b_wjets2("rfv_"+region_proc_cr+"2","Background yield in control region, bin 2","@0*@1",RooArgList(TF2,rrvbc_sr2_wjets.at(1)));
  RooFormulaVar rfv_wenu_2b_wjets3("rfv_"+region_proc_cr+"3","Background yield in control region, bin 3","@0*@1",RooArgList(TF3,rrvbc_sr2_wjets.at(2)));
  RooFormulaVar rfv_wenu_2b_wjets4("rfv_"+region_proc_cr+"4","Background yield in control region, bin 4","@0*@1",RooArgList(TF4,rrvbc_sr2_wjets.at(3)));



  // --------------------------------------------------------------
  // ------------------------WJets (muon ) Control region ---------
  // --------------------------------------------------------------

  RooArgList ral_wenu_2b_wjets;
  ral_wenu_2b_wjets.add(rfv_wenu_2b_wjets1);
  ral_wenu_2b_wjets.add(rfv_wenu_2b_wjets2);
  ral_wenu_2b_wjets.add(rfv_wenu_2b_wjets3);
  ral_wenu_2b_wjets.add(rfv_wenu_2b_wjets4);


  RooParametricHist rph_wenu_2b_wjets("rph_"+region_proc_cr, "Background PDF in control region",met,ral_wenu_2b_wjets, *h_sr2_data);
  RooAddition rph_wenu_2b_wjets_norm("rph_"+region_proc_cr+"_norm","Total Number of events from background in control region", ral_wenu_2b_wjets);

  wspace.import(rph_wenu_2b_wjets);
  wspace.import(rph_wenu_2b_wjets_norm ,RooFit::RecycleConflictNodes());


}




void PrepareWS_withSyst(){
  ///afs/cern.ch/work/p/ptiwari/public/bbDM/WCr_Split/AllMETHistos.root
  TString inputfile   = "AllMETHistos.root";
  TString outputfile  = "bbDM_WS.root";
  TString year        = "_2016";
  TString version     = "_V0";

  int met_low = 200;
  int met_hi = 1000;
  Double_t bins[]={200,250,350,500,1000};
  Int_t  binnum = sizeof(bins)/sizeof(Double_t) - 1;

  // As usual, load the combine library to get access to the RooParametricHist
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  // Output file and workspace
  TFile* fOut = OpenRootFile(outputfile,"RECREATE");
  RooWorkspace wspace("ws_bbDM","ws_bbDM");

  // A search in a MET tail, define MET as our variable
  RooRealVar met("met","p_{T}^{miss}",met_low, met_hi);
  RooArgList vars(met);

  std::cout<<" debug 2" <<std::endl;


  // Open input file with all the histograms.
  TFile* fin = OpenRootFile(inputfile);



  // this histogram is just for the binning
  // --- commented on 5 Feb to see if the limis becomes same when using the opriginal data histogram
  TH1F* h_sr1_data = (TH1F*) fin->Get("bbDM2016_1b_SR_data_obs");
  TH1F* h_sr2_data = (TH1F*) fin->Get("bbDM2016_2b_SR_data_obs");

  //the following lines create a freely floating parameter for each of our bins (in this example, there are only 4 bins, defined for our observable met.
  // In this case we vary the normalisation in each bin of the background from N/3 to 3*N,
  // e.g. if actual content in the histogram is 55 then we initialize
  // it with 55 and vary it from 55/3 to 55*3. which is very close to freely floating. This can be checked if this works for the cases when bin content is very low,
  // specially in the tails and can be changed easily .



  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W enu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
   */


  std::cout<<" calling function for Wenu"<<std::endl;

  // Get the wjets histogram in signal region
  TH1F* h_sr1_wjets = (TH1F*) fin->Get("bbDM2016_1b_SR_wjets");
  TH1F* h_sr2_wjets = (TH1F*) fin->Get("bbDM2016_2b_SR_wjets");

  // Get the wjets histogram in the Wenu CR
  TH1F* h_wenu_1b_wjets = (TH1F*) fin->Get("bbDM2016_1b_WENUCR_wjets");
  TH1F* h_wenu_2b_wjets = (TH1F*) fin->Get("bbDM2016_2b_WENUCR_wjets");

  std::cout<<" integral of wenu : "<<h_sr2_wjets->Integral() <<"  "<<h_wenu_2b_wjets->Integral()<<std::endl;
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_wjets, h_wenu_1b_wjets, h_sr1_data, wspace, "1b_WE_wjets", "1b_SR_e_wjets",  fOut);
  createRegion(met, h_sr2_wjets, h_wenu_2b_wjets, h_sr2_data, wspace, "2b_WE_wjets", "2b_SR_e_wjets",  fOut);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W munu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
    */

  std::cout<<" calling function for Wmunu"<<std::endl;
  // Get the wjets hostogram in the Wmunu CR
  TH1F* h_wmunu_1b_wjets = (TH1F*) fin->Get("bbDM2016_1b_WMUNUCR_wjets");
  TH1F* h_wmunu_2b_wjets = (TH1F*) fin->Get("bbDM2016_2b_WMUNUCR_wjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_wjets, h_wmunu_1b_wjets, h_sr2_data, wspace, "1b_WMU_wjets", "1b_SR_mu_wjets",  fOut);
  createRegion(met, h_sr2_wjets, h_wmunu_2b_wjets, h_sr2_data, wspace, "2b_WMU_wjets", "2b_SR_mu_wjets",  fOut);



  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top mu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


    std::cout<<" calling function for Top mu"<<std::endl;
  TH1F* h_sr1_top = (TH1F*) fin->Get("bbDM2016_1b_SR_tt");
  TH1F* h_sr2_top = (TH1F*) fin->Get("bbDM2016_2b_SR_tt");
  // Get the top hostogram in the Top mu CR
  TH1F* h_topmu_1b_top = (TH1F*) fin->Get("bbDM2016_1b_TOPMUNUCR_tt");
  TH1F* h_topmu_2b_top = (TH1F*) fin->Get("bbDM2016_2b_TOPMUNUCR_tt");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_top, h_topmu_1b_top, h_sr1_data, wspace, "1b_TOPMU_tt", "1b_SR_mu_tt",  fOut);
  createRegion(met, h_sr2_top, h_topmu_2b_top, h_sr2_data, wspace, "2b_TOPMU_tt", "2b_SR_mu_tt",  fOut);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top e CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


    std::cout<<" calling function for Top e"<<std::endl;
  // Get the top hostogram in the Top mu CR
  TH1F* h_tope_1b_top = (TH1F*) fin->Get("bbDM2016_1b_TOPENUCR_tt");
  TH1F* h_tope_2b_top = (TH1F*) fin->Get("bbDM2016_2b_TOPENUCR_tt");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_top, h_tope_1b_top, h_sr1_data, wspace, "1b_TOPE_tt", "1b_SR_e_tt",  fOut);
  createRegion(met, h_sr2_top, h_tope_2b_top, h_sr2_data, wspace, "2b_TOPE_tt", "2b_SR_e_tt",  fOut);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zmumu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


  std::cout<<" calling function for Zmumu"<<std::endl;
  TH1F* h_sr1_Z = (TH1F*) fin->Get("bbDM2016_1b_SR_zjets");
  TH1F* h_sr2_Z = (TH1F*) fin->Get("bbDM2016_2b_SR_zjets");
  // Get the top hostogram in the Top mu CR
  TH1F* h_Zmumu_1b_Z = (TH1F*) fin->Get("bbDM2016_1b_ZMUMUCR_dyjets");
  TH1F* h_Zmumu_2b_Z = (TH1F*) fin->Get("bbDM2016_2b_ZMUMUCR_dyjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_Z, h_Zmumu_1b_Z, h_sr1_data, wspace, "1b_ZMUMU_dyjets", "1b_SR_zjets",  fOut);
  createRegion(met, h_sr2_Z, h_Zmumu_2b_Z, h_sr2_data, wspace, "2b_ZMUMU_dyjets", "2b_SR_zjets",  fOut);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zee CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


  // Get the top hostogram in the Top mu CR
  TH1F* h_Zee_2b_Z = (TH1F*) fin->Get("bbDM2016_2b_ZEECR_dyjets");
  TH1F* h_Zee_1b_Z = (TH1F*) fin->Get("bbDM2016_1b_ZEECR_dyjets");
  // Create all the inputs needed for this CR
  createRegion(met, h_sr1_Z, h_Zee_1b_Z, h_sr1_data, wspace, "1b_ZEE_dyjets", "1b_SR_dyjets",  fOut);
  createRegion(met, h_sr2_Z, h_Zee_2b_Z, h_sr2_data, wspace, "2b_ZEE_dyjets", "2b_SR_dyjets",  fOut);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Signal -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


  int signalpoint_600[]={50,100,150,200,250,300,350,400,500};
  Int_t  nsig_600 = sizeof(signalpoint_600)/sizeof(int);
  TString mps_600;
  for (auto is=0; is<nsig_600; is++){
    mps_600.Form("%d",signalpoint_600[is]);
    addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_SR_2HDMa_Ma"+mps_600+"_MChi1_MA600_tb35_st_0p7" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_SR_2HDMa_Ma"+mps_600+"_MChi1_MA600_tb35_st_0p7" ) );
  }
  int signalpoint_1200[]={10,50,150,200,250,350,400,450,500,700,750,1000};
  Int_t  nsig_1200 = sizeof(signalpoint_1200)/sizeof(int);
  TString mps_1200;
  for (auto is=0; is<nsig_1200; is++){
    mps_1200.Form("%d",signalpoint_1200[is]);
    addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_SR_2HDMa_Ma"+mps_1200+"_MChi1_MA1200_tb35_st_0p7" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_SR_2HDMa_Ma"+mps_1200+"_MChi1_MA1200_tb35_st_0p7" ) );
  }

  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_SR_data_obs" ) );

  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_TOPENUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_TOPMUNUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_WENUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_WMUNUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_ZEECR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_2b_ZMUMUCR_data_obs" ) );

  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_SR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_TOPENUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_TOPMUNUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_WENUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_WMUNUCR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_ZEECR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("bbDM2016_1b_ZMUMUCR_data_obs" ) );


 // all other histograms
  std::vector<TString> regions;
  regions.push_back("SR");
  regions.push_back("TOPENUCR");
  regions.push_back("TOPMUNUCR");
  regions.push_back("WENUCR");
  regions.push_back("WMUNUCR");
  regions.push_back("ZEECR");
  regions.push_back("ZMUMUCR");


  std::vector<TString> process;

  process.push_back("diboson");
  process.push_back("gjets");
  process.push_back("qcd");
  process.push_back("zjets");
  process.push_back("wjets");
  process.push_back("dyjets");
  process.push_back("tt");
  process.push_back("singlet");


  std::vector<TString> category;
  category.push_back("bbDM2016_1b_");
  category.push_back("bbDM2016_2b_");

  TString tempname;
  for (auto ir=0; ir<regions.size(); ir++){

    for (auto ip=0; ip<process.size(); ip++){

      for (auto ic=0; ic<category.size(); ic++){
	if (process[ip] == "wjets") continue ;
	tempname = category[ic] + regions[ir] + "_" +  process[ip];
	//tempname = regions[ir] + "_" + category[ic] + "_" + process[ip];
	std::cout<<" saving "<<tempname<<std::endl;
	addTemplate(wspace, vars, (TH1F*) fin->Get(tempname)  );


      }
    }
  }



  // write the workspace at the very end, once everthing has been imported to the workspace
  fOut->cd();
  wspace.Write();

}
