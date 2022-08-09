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
    rrvV_.push_back(RooRealVar(name+postfix,"Background yield in signal region, bin 1", bcs[i], 0.2*bcs[i], 5*bcs[i]));
    
  }
  
  return rrvV_;
}

void plotTFPrefit(){
  
}

void plotSystPrefit(){
  
}


std::vector<TH1F*> h_vec_tf;

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
		  TString anacat_){
  
  anacat_ = "_"+anacat_;
  RooArgList vars(met);

  /* Get the bin content of each bin of the histogram in a vector which can be used later */ 
  std::vector<float> bincontents_sr_bkg = GetBinContents(h_sr_bkg);
  
  // This will create the RooRealVar with 0 to 10*bin content  range.
  // The bkg contribution in SR is RooRealVar and then converted to RooArgList

  // create a vector of RooRealVar, this is needed because I didn't find  way to retrive the RooRealVar back from the RooArgList
  std::vector<RooRealVar> rrvbc_sr_bkg = GetRooRealVar(bincontents_sr_bkg, "rrvbc_"+region_proc_sr+anacat_);
  
  RooArgList ralbc_sr_bkg; // this can be converted to a for loop
  ralbc_sr_bkg.add(rrvbc_sr_bkg[0]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[1]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[2]);
  ralbc_sr_bkg.add(rrvbc_sr_bkg[3]);
  
  // Create a RooParametericHist which contains those yields, last argument is just for the binning, we can use the data TH1 for that
  // RPH for the bkg yield in the SR 
  RooParametricHist rph_sr_bkg("rph_"+region_proc_sr+anacat_, " "+region_proc_sr+" PDF in signal region "+anacat_,met,ralbc_sr_bkg, *h_sr_data);
  

  // Always include a _norm term which should be the sum of the yields (thats how combine likes to play with pdfs)
  // not sure yet why is this needed? 
  RooAddition rph_sr_bkg_norm("rph_"+region_proc_sr+anacat_+"_norm","Total Number of events from background in signal region "+anacat_,ralbc_sr_bkg);


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
  RooDataHist dh_cr_bkg("dh_"+region_proc_cr+anacat_,"dh_"+region_proc_cr+anacat_, vars, h_cr_bkg);
  
  // another copy fo the wjets in wenu CR for division and saving thr TFs central value. 
  // transfer factor is defined as ratio of TF =  bkg in CR / bkg in SR 
  
  std::cout<<" datahist created "<<h_cr_bkg->GetName()<<" "<<h_sr_bkg->GetName()
	   <<" "<<h_cr_bkg->GetNbinsX()<<" "<<h_sr_bkg->GetNbinsX()<<std::endl;
  
  TH1F* htf_cr_bkg = (TH1F*) h_cr_bkg->Clone();
  htf_cr_bkg->Divide(h_sr_bkg);

  // writing this to the root file for presentation purpose. 
  h_vec_tf.push_back(htf_cr_bkg);
  
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
  
  
  // Get bin content of each bin of this ratio histogram and save it in the RooRealVar which will be used later for the Actual Transfer Factor with effect of Nuisance parameters included 
  // idelaly each of these rooreal var in following vector should be setConstat(1) otherwise it may be treated as free parameter however it should be fixed. 
  std::vector <float> bincontents_htf_cr_bkg =  GetBinContents(htf_cr_bkg);
  
  RooRealVar tf1 ("tf1_"+region_proc_cr+anacat_,"tf1_"+region_proc_cr+anacat_,bincontents_htf_cr_bkg[0]) ;
  RooRealVar tf2 ("tf2_"+region_proc_cr+anacat_,"tf2_"+region_proc_cr+anacat_,bincontents_htf_cr_bkg[1]) ;
  RooRealVar tf3 ("tf3_"+region_proc_cr+anacat_,"tf3_"+region_proc_cr+anacat_,bincontents_htf_cr_bkg[2]) ;
  RooRealVar tf4 ("tf4_"+region_proc_cr+anacat_,"tf4_"+region_proc_cr+anacat_,bincontents_htf_cr_bkg[3]) ;
  

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
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(1) / htf_cr_bkg->GetBinContent(1) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(2) / htf_cr_bkg->GetBinContent(2) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(3) / htf_cr_bkg->GetBinContent(3) ) ;
  tf_stats_err_vector.push_back(htf_cr_bkg->GetBinError(4) / htf_cr_bkg->GetBinContent(4) ) ;
  
  std::cout<<" tf stats errors "
	   <<" "<<tf_stats_err_vector[0]
	   <<" "<<tf_stats_err_vector[1]
	   <<" "<<tf_stats_err_vector[2]
	   <<" "<<tf_stats_err_vector[3]
	   <<std::endl;
    
  
  
  int syst_counter = 0;
  
  TString rfv_bin1 = Form("@%d*",syst_counter++); // this is transfer factor  ,  ++ is needed so that the counter is increamented automatically after its usage 
  TString rfv_bin2 = rfv_bin1; // yes this is correct: this is to write @0 for each bin and at next occurenace it will become @1 and so on, 
  TString rfv_bin3 = rfv_bin1;
  TString rfv_bin4 = rfv_bin1;
  
  std::vector<std::string> rfv_tf_stats_err_vector = createnuisance(tf_stats_err_vector, 4, syst_counter++);
    
  rfv_bin1  += rfv_tf_stats_err_vector[0] ;
  rfv_bin2  += rfv_tf_stats_err_vector[1] ;
  rfv_bin3  += rfv_tf_stats_err_vector[2] ;
  rfv_bin4  += rfv_tf_stats_err_vector[3] ;
  
  //RooRealVar rrv_stats_err_bin1("rrv_stats_err_"+region_proc_cr+"_bin1", "rrv_stats_err_"+region_proc_cr+"_bin1",0);
  //RooRealVar rrv_stats_err_bin2("rrv_stats_err_"+region_proc_cr+"_bin2", "rrv_stats_err_"+region_proc_cr+"_bin2",0);
  //RooRealVar rrv_stats_err_bin3("rrv_stats_err_"+region_proc_cr+"_bin3", "rrv_stats_err_"+region_proc_cr+"_bin3",0);
  //RooRealVar rrv_stats_err_bin4("rrv_stats_err_"+region_proc_cr+"_bin4", "rrv_stats_err_"+region_proc_cr+"_bin4",0);

  // allow the stats error to vary fom 0 to  2* sigma 
  RooRealVar rrv_stats_err_bin1("rrv_stats_err_"+region_proc_cr+anacat_+"_bin1", "rrv_stats_err_"+region_proc_cr+"_bin1",tf_stats_err_vector[0],  0,  2.*tf_stats_err_vector[0]);
  RooRealVar rrv_stats_err_bin2("rrv_stats_err_"+region_proc_cr+anacat_+"_bin2", "rrv_stats_err_"+region_proc_cr+"_bin2",tf_stats_err_vector[1],  0,  2.*tf_stats_err_vector[1]);
  RooRealVar rrv_stats_err_bin3("rrv_stats_err_"+region_proc_cr+anacat_+"_bin3", "rrv_stats_err_"+region_proc_cr+"_bin3",tf_stats_err_vector[2],  0,  2.*tf_stats_err_vector[2]);
  RooRealVar rrv_stats_err_bin4("rrv_stats_err_"+region_proc_cr+anacat_+"_bin4", "rrv_stats_err_"+region_proc_cr+"_bin4",tf_stats_err_vector[3],  0,  2.*tf_stats_err_vector[3]);
  
  RooArgList ral_bin1;
  RooArgList ral_bin2;
  RooArgList ral_bin3;
  RooArgList ral_bin4;
  
  
  ral_bin1.add(tf1);
  ral_bin2.add(tf2);
  ral_bin3.add(tf3);
  ral_bin4.add(tf4);


  ral_bin1.add(rrv_stats_err_bin1);
  ral_bin2.add(rrv_stats_err_bin2);
  ral_bin3.add(rrv_stats_err_bin3);
  ral_bin4.add(rrv_stats_err_bin4);
  
  
  RooRealVar* rrv_syst;
  //RooRealVar* rrv_syst_bin2;
  //RooRealVar* rrv_syst_bin3;
  //RooRealVar* rrv_syst_bin4;
  for (int isys=0; isys < (int) nuisIndex.size(); isys++){
    std::vector<std::string> add_logN_systematic = createnuisance(nuisanceValue[nuisIndex[isys]], 4, syst_counter++);
    //for (int i =0; i<4; i++)  std::cout<<" add_logN_systematic = "<<add_logN_systematic[i]<<std::endl;
    rfv_bin1 += "*"+add_logN_systematic[0];
    rfv_bin2 += "*"+add_logN_systematic[1];
    rfv_bin3 += "*"+add_logN_systematic[2];
    rfv_bin4 += "*"+add_logN_systematic[3];
    
    std::cout<<" bin 1 stats unc "<< rfv_bin1<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 2 stats unc "<< rfv_bin2<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 3 stats unc "<< rfv_bin3<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    std::cout<<" bin 4 stats unc "<< rfv_bin4<<" after including "<<nuisanceName[nuisIndex[isys]]<<std::endl;
    
    //rrv_syst = new RooRealVar("rrv_"+nuisanceName[nuisIndex[isys]], "rrv_"+nuisanceName[nuisIndex[isys]], 0);
    //rrv_syst = new RooRealVar("rrv_"+nuisanceName[nuisIndex[isys]], "rrv_"+nuisanceName[nuisIndex[isys]], nuisanceValue[nuisIndex[isys]], 0., 5*nuisanceValue[nuisIndex[isys]]);
    rrv_syst = new RooRealVar(nuisanceName[nuisIndex[isys]]+anacat_, "rrv_"+nuisanceName[nuisIndex[isys]], nuisanceValue[nuisIndex[isys]], 0., 5*nuisanceValue[nuisIndex[isys]]);
    
    ral_bin1.add(*rrv_syst);
    ral_bin2.add(*rrv_syst);
    ral_bin3.add(*rrv_syst);
    ral_bin4.add(*rrv_syst); // it has to be pointer for some reason, otherwise it gives seg fault, not sure yet, why? 
    
  }
  
  std::cout<<" bins already included in the lists "<<ral_bin1<<std::endl;
  /*
    RooFormulaVar TF1("TF1"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf1));
  RooFormulaVar TF2("TF2"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf2));
  RooFormulaVar TF3("TF3"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf3));
  RooFormulaVar TF4("TF4"+region_proc_cr,"Transfer factor","@2*TMath::Power(1.01,@0)*TMath::Power(1.02,@1)",RooArgList(efficiency,acceptance,tf4));
  */

  std::cout<<" RAL = "<<ral_bin1<<std::endl;
  RooFormulaVar TF1("TF1"+region_proc_cr+anacat_,"Transfer factor",rfv_bin1, ral_bin1); //RooArgList(efficiency,acceptance,tf2,tf3));
  RooFormulaVar TF2("TF2"+region_proc_cr+anacat_,"Transfer factor",rfv_bin2, ral_bin2);
  RooFormulaVar TF3("TF3"+region_proc_cr+anacat_,"Transfer factor",rfv_bin3, ral_bin3);
  RooFormulaVar TF4("TF4"+region_proc_cr+anacat_,"Transfer factor",rfv_bin4, ral_bin4);
  /*
    Then need to make each bin of the background in the control region a function of the background in the signal and the transfer factor - 
    i.e NCR=NSR x TF
  */
  std::cout<<" TF done "<<std::endl;
  
  

  RooFormulaVar rfv_cr_bkg1("rfv_"+region_proc_cr+"1"+anacat_,"Background yield in control region, bin 1","@0*@1",RooArgList(TF1, rrvbc_sr_bkg.at(0)));
  RooFormulaVar rfv_cr_bkg2("rfv_"+region_proc_cr+"2"+anacat_,"Background yield in control region, bin 2","@0*@1",RooArgList(TF2,rrvbc_sr_bkg.at(1)));
  RooFormulaVar rfv_cr_bkg3("rfv_"+region_proc_cr+"3"+anacat_,"Background yield in control region, bin 3","@0*@1",RooArgList(TF3,rrvbc_sr_bkg.at(2)));
  RooFormulaVar rfv_cr_bkg4("rfv_"+region_proc_cr+"4"+anacat_,"Background yield in control region, bin 4","@0*@1",RooArgList(TF4,rrvbc_sr_bkg.at(3)));
  


  // --------------------------------------------------------------
  // ------------------------WJets (muon ) Control region ---------
  // --------------------------------------------------------------
  
  RooArgList ral_cr_bkg;
  ral_cr_bkg.add(rfv_cr_bkg1);
  ral_cr_bkg.add(rfv_cr_bkg2);
  ral_cr_bkg.add(rfv_cr_bkg3);
  ral_cr_bkg.add(rfv_cr_bkg4);
    
  
  std::cout<<" before rph "<<std::endl;
  RooParametricHist rph_cr_bkg("rph_"+region_proc_cr+anacat_, "Background PDF in control region",met,ral_cr_bkg, *h_sr_data);
  RooAddition rph_cr_bkg_norm("rph_"+region_proc_cr+anacat_+"_norm","Total Number of events from background in control region", ral_cr_bkg);
  
  std::cout<<" before rph import "<<std::endl;
  wspace.import(rph_cr_bkg);
  std::cout<<" before rph norm import"<<std::endl;
  wspace.import(rph_cr_bkg_norm ,RooFit::RecycleConflictNodes());

  
  

}




void PrepareWS_withnuisance(TString model_="monoHbb",TString analysiscategory_="merged", TString mode__ = "RECREATE", TString inputdir=".", TString inputfile="AllMETHistos.root", TString year="2016"){
  TString anacat_ = analysiscategory_;
  ///afs/cern.ch/work/p/ptiwari/public/bbDM/WCr_Split/AllMETHistos.root
  //TString inputdir    = ""
  
  //TString inputfile   = "AllMETHistos_v16_06_04_04.root";
  //TString year        = "2016";
  TString outputfile  = model_+"_"+year+"_WS.root";
  TString cat__ =  analysiscategory_;
  
  //if (analysiscategory_=="merged") cat__ = "B";
  //if (analysiscategory_=="resolved") cat__ = "R";
  //if (analysiscategory_=="combined") cat__ = "C";
  
  bool debug__ = true; 
  
  //if (debug__){

  TString AnaYearCat  = model_ +  year + "_" + cat__ +"_" ;
  std::cout<<" AnaYearCat = "<<AnaYearCat<<std::endl;
  TString version     = "_V0";
  bool usebkgsum = false;
  int met_low = 200;
  int met_hi = 1000;
  h_vec_tf.clear();
    
  Double_t bins[]={200, 250, 350, 500, 1000};
  Int_t  binnum = sizeof(bins)/sizeof(Double_t) - 1;
  
  // As usual, load the combine library to get access to the RooParametricHist
  gSystem->Load("libHiggsAnalysisCombinedLimit.so");
  // Output file and workspace 
  TFile* fOut = OpenRootFile(outputfile,mode__);
  
  TString workspacename = "ws_"+model_+"_"+analysiscategory_+"_"+year;
  TString workspacetitle = "work space for year "+year+", analysis "+model_+", category "+analysiscategory_;
  RooWorkspace wspace(workspacename,workspacetitle);

  // A search in a MET tail, define MET as our variable 
  RooRealVar met("met","p_{T}^{miss}",met_low, met_hi);
  RooArgList vars(met);
  
  std::cout<<" debug 2" <<std::endl;

  
  // Open input file with all the histograms. 
  TFile* fin = OpenRootFile(inputdir+"/"+inputfile);

  

  // this histogram is just for the binning 
  // --- commented on 5 Feb to see if the limis becomes same when using the opriginal data histogram
  

  TH1F* h_sr_data = (TH1F*) fin->Get(AnaYearCat+"SR_bkgSum");
  
  //the following lines create a freely floating parameter for each of our bins (in this example, there are only 4 bins, defined for our observable met.
  // In this case we vary the normalisation in each bin of the background from N/3 to 3*N, 
  // e.g. if actual content in the histogram is 55 then we initialize
  // it with 55 and vary it from 55/3 to 55*3. which is very close to freely floating. This can be checked if this works for the cases when bin content is very low, 
  // specially in the tails and can be changed easily . 
 
  
    
  std::vector <TString> nuisanceName;
  std::vector <float> nuisanceValue;
  
  nuisanceName.clear();    nuisanceValue.clear();
  TString nuisancePostfix = "CMS2016_scale_";
  nuisanceValue.clear();
  // these number are temporary at this moment, these has to be updated 
  nuisanceName.push_back(nuisancePostfix+"m");             nuisanceValue.push_back(0.02);  // 0 
  nuisanceName.push_back(nuisancePostfix+"e");              nuisanceValue.push_back(0.03);  // 1 
  nuisanceName.push_back("eletrigeff"+nuisancePostfix);          nuisanceValue.push_back(0.04);  // 2 
  
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top mu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  
  
  std::cout<<" calling function for Top mu"<<std::endl;
  TH1F* h_sr_top = (TH1F*) fin->Get(AnaYearCat+"SR_tt");
  // Get the top hostogram in the Top mu CR
  TH1F* h_topmu_2b_top = (TH1F*) fin->Get(AnaYearCat+"TOPMU_tt");
  
  
  // Create all the inputs needed for this CR 
  // list of systematics for Top mu CR 
  std::vector<int> nuisIndex; nuisIndex.clear(); // this is the index of nuisances which are to be used for mu CR 
  nuisIndex.push_back(0); // muon efficiency 
  

  // mu efficiency for Top mu CR 
  createRegion(met, h_sr_top, h_topmu_2b_top, h_sr_data, wspace, "TOPMU_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_);

  
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top e CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */


  nuisIndex.clear();
  nuisIndex.push_back(1); 
  nuisIndex.push_back(2); 
    std::cout<<" calling function for Top e"<<std::endl;
  // Get the top hostogram in the Top mu CR
  TH1F* h_tope_2b_top = (TH1F*) fin->Get(AnaYearCat+"TOPE_tt");
  // Create all the inputs needed for this CR 
  createRegion(met, h_sr_top, h_tope_2b_top, h_sr_data, wspace, "TOPE_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue,anacat_);

  
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W enu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
   */



  nuisIndex.clear();
  nuisIndex.push_back(1);
  nuisIndex.push_back(2);

    std::cout<<" calling function for Wenu"<<std::endl;
  
  // Get the wjets histogram in signal region
  TH1F* h_sr_wjets = (TH1F*) fin->Get(AnaYearCat+"SR_wjets");
  
  // Get the wjets hostogram in the Wenu CR
  TH1F* h_wenu_2b_wjets = (TH1F*) fin->Get(AnaYearCat+"WE_wjets");
  
  std::cout<<" integral of wenu : "<<h_sr_wjets->Integral() <<"  "<<h_wenu_2b_wjets->Integral()<<std::endl;
  // Create all the inputs needed for this CR 
  createRegion(met, h_sr_wjets, h_wenu_2b_wjets, h_sr_data, wspace, "WE_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_);


  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W munu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
    */

  nuisIndex.clear();
  nuisIndex.push_back(0);

  std::cout<<" calling function for Wmunu"<<std::endl;
  // Get the wjets hostogram in the Wmunu CR
  TH1F* h_wmunu_2b_wjets = (TH1F*) fin->Get(AnaYearCat+"WMU_wjets");
  // Create all the inputs needed for this CR 
  createRegion(met, h_sr_wjets, h_wmunu_2b_wjets, h_sr_data, wspace, "WMU_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_);
  

  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zmumu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  nuisIndex.clear();
  nuisIndex.push_back(0);
  
  std::cout<<" calling function for Zmumu"<<std::endl;
  TH1F* h_sr_Z = (TH1F*) fin->Get(AnaYearCat+"SR_zjets");
  // Get the top hostogram in the Top mu CR
  TH1F* h_Zmumu_2b_Z = (TH1F*) fin->Get(AnaYearCat+"ZMUMU_dyjets");
  // Create all the inputs needed for this CR 
  createRegion(met, h_sr_Z, h_Zmumu_2b_Z, h_sr_data, wspace, "ZMUMU_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_);

  
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zee CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */  

  nuisIndex.clear();
  nuisIndex.push_back(1);
  nuisIndex.push_back(2);

    // Get the top hostogram in the Top mu CR
  TH1F* h_Zee_2b_Z = (TH1F*) fin->Get(AnaYearCat+"ZEE_dyjets");
  // Create all the inputs needed for this CR 
  createRegion(met, h_sr_Z, h_Zee_2b_Z, h_sr_data, wspace, "ZEE_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_);

  
  std::cout<<" all crs done "<<std::endl;


  //} // end of the debug__
  /*
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Signal -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  */

  std::vector<int> signalpoint;
  signalpoint.clear();
  if (year!="2016"){
    signalpoint.push_back(10);
    signalpoint.push_back(450);
  }
  
  if (year=="2017" || year == "2018" || year == "2016") {
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
  mApoint.push_back(1200.);
  
  
  Int_t  nsig = signalpoint.size();
  
  TString mps;
  TString mAs;
  for (auto is=0; is<nsig; is++){
    
    for (auto imA=0; imA<mApoint.size(); imA++){
      mAs.Form("%d",mApoint[imA]);
      mps.Form("%d",signalpoint[is]);
      if (year=="2016"){
	if ( (signalpoint[is] == 100) && (mApoint[imA] == 1200) ) continue; 
	if ( (signalpoint[is] == 300) && (mApoint[imA] == 1200) ) continue; 
      }
      TString signalname = AnaYearCat+"SR_2HDMa_Ma"+mps+"_MChi1_MA"+mAs+"_tb35_st_0p7";
      std::cout<<" signal histogram :"<<signalname<<std::endl;
      
      addTemplate(wspace, vars, (TH1F*) fin->Get(signalname ) );
    }
  }
  
  
  
  if (!usebkgsum){
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"SR_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPE_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"TOPMU_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WE_data_obs" ) );
    addTemplate(wspace, vars, (TH1F*) fin->Get(AnaYearCat+"WMU_data_obs" ) );
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
  
  /*
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_SR_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_TOPE_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_TOPMU_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_WE_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_WMU_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_ZEE_data_obs" ) );
  addTemplate(wspace, vars, (TH1F*) fin->Get("monoHbb2017_R_ZMUMU_data_obs" ) );
  */
 
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
  //category.push_back("monoHbb2017_R_");
  category.push_back(AnaYearCat);
  
  TString tempname;
  for (auto ir=0; ir<regions.size(); ir++){

    for (auto ip=0; ip<process.size(); ip++){

      for (auto ic=0; ic<category.size(); ic++){
	if (process[ip] == "wjets" && ( (regions[ir] =="WE") || (regions[ir] =="WMU") ) ) continue ;
	if (process[ip] == "tt" && ( (regions[ir] =="TOPE") || (regions[ir] =="TOPMU") ) ) continue ;
	
	tempname = category[ic] + regions[ir] + "_" +  process[ip];
	//tempname = regions[ir] + "_" + category[ic] + "_" + process[ip];
	std::cout<<" saving "<<tempname<<std::endl;
	addTemplate(wspace, vars, (TH1F*) fin->Get(tempname)  );
	std::cout<<" ........ saved"<<std::endl;
	
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
