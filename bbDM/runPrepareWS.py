
import ROOT as rt
import optparse
import os


## functions
def OpenRootFile(filename, mode="READ"):
  f = rt.TFile (filename, mode)
  return f

def GetBinContents(h):
  bcs = []
  print(" histogram name :", h.GetName())
  nbinsx = int(h.GetNbinsX())
  for ibin in range(1,nbinsx+1):
    bcs.append(h.GetBinContent(ibin))
  return bcs

def addTemplate(ws, vars, hist, outhistnamestat=""):
  print(" name = ", hist.GetName())
  if len(outhistnamestat)==0:
    outhistnamestat=hist.GetName()
  rhist = rt.RooDataHist(outhistnamestat, outhistnamestat,  vars, hist)
  print(" integral of the histogram for ",hist.GetName()," is ",rhist.sumEntries(),"  ",hist.Integral()," bins: ",hist.GetNbinsX())
  for ibin in range(1, hist.GetXaxis().GetNbins()+1):
    if (hist.GetBinContent(ibin)<=0):
      print(" histogram: ",hist.GetName()," has negative bin content",ibin," ",hist.GetBinContent(ibin))
  getattr(ws,'import')(rhist)


def GetRooRealVar(bcs, name, year=""):
  rrvV_ = []
  for i in range(len(bcs)):
    # fix the naming here using some automation  and also in the next function
    # std::cout<<" name inside GetRooRealVar = "<<name+postfix<<std::endl;
    rrvV_.append(rt.RooRealVar(name+str(i+1)+"_"+year,"Background yield in signal region, bin 1", bcs[i], 0.2*bcs[i], 2*bcs[i]))
  return rrvV_

def createnuisance(value_, nbins, nuisanceCounter):
  logN_nuisance_vec = []
  for i in range(nbins):
    if isinstance(value_, float):
      logN_nuisance_1bin = "TMath::Power(1+"+str(value_)+",@"+str(nuisanceCounter)+")";   ## this gives a string like  "TMath::Power(1+0.15,@0)"
    elif isinstance(value_, list):
      logN_nuisance_1bin = "TMath::Power(1+"+str(value_[i])+",@"+str(nuisanceCounter)+")";   ## this gives a string like  "TMath::Power(1+0.15,@0)"
    logN_nuisance_vec.append(logN_nuisance_1bin)
  return logN_nuisance_vec


def createRegion(h_vec_tf,met,h_sr_bkg ,h_cr_bkg,h_sr_data,wspace,region_proc_cr,region_proc_sr,fOut,nuisIndex,nuisanceName,
		   nuisanceValue,anacat_,year_, fIn_,crname):
  anacat_orig=anacat_
  anacat_ = "_"+anacat_
  vars = rt.RooArgList(met)

  ## Get the bin content of each bin of the histogram in a vector which can be used later */
  bincontents_sr_bkg = GetBinContents(h_sr_bkg)

  # This will create the RooRealVar with 0 to 10*bin content  range.
  # The bkg contribution in SR is RooRealVar and then converted to RooArgList

  # create a vector of RooRealVar,this is needed because I didn't find  way to retrive the RooRealVar back from the RooArgList
  rrvbc_sr_bkg_ = GetRooRealVar(bincontents_sr_bkg,"rrvbc_"+region_proc_sr+anacat_,year_)
  nHistbins=len(bincontents_sr_bkg)

  ralbc_sr_bkg = rt.RooArgList() # this can be converted to a for loop
  rrvbc_sr_bkg = rt.RooArgList()
  for i in range(len(rrvbc_sr_bkg_)):
    ralbc_sr_bkg.add(rrvbc_sr_bkg_[i])
    rrvbc_sr_bkg.add(rrvbc_sr_bkg_[i])

  # Create a RooParametericHist which contains those yields,last argument is just for the binning,we can use the data TH1 for that
  # RPH for the bkg yield in the SR
  rph_sr_bkg = rt.RooParametricHist("rph_"+region_proc_sr+anacat_+"_"+year_," "+region_proc_sr+" PDF in signal region "+anacat_+year_,met,ralbc_sr_bkg,h_sr_data)

  # Always include a _norm term which should be the sum of the yields (thats how combine likes to play with pdfs)
  # not sure yet why is this needed?
  rph_sr_bkg_norm = rt.RooAddition("rph_"+region_proc_sr+anacat_+"_"+year_+"_norm","Total Number of events from background in signal region "+anacat_+year_,ralbc_sr_bkg)

  getattr(wspace,'import')(rph_sr_bkg)
  getattr(wspace,'import')(rph_sr_bkg_norm,rt.RooFit.RecycleConflictNodes())

  print(" rph for bkg in SR is imported in the WS")

  '''
  For the control region,the background process will be dependent on the yields of the background in the signal region using a transfer factor.
  The transfer factor TF must account for acceptance/efficiency etc differences in the signal to control regions.
  In this case we define the transfer factor as: ratio of the WJets (electron) yield in the WJets control region and
  WJets in the Signal region.

  For each bin a transfer factor is calculated and the nuisance parameters are associated with this.

  We could imagine that the transfer factor could be associated with some uncertainty - lets say a 1% uncertainty due to efficiency and 2% due to acceptance.
  We need to make nuisance parameters ourselves to model this and give them a nominal value of 0.

  We need to make the transfer factor a function of these parameters since variations in these uncertainties will lead to variations of the transfer factor. Here we've assumed Log-normal effects (i.e the same as putting lnN in the CR datacard) but we could use any function which could be used to parameterise the effect - eg if the systematic is due to some alternate template,we could use polynomials for example.
  '''


  # check the anme and integral of bkg histogram in CR
  print(" h_cr_bkg: ",h_cr_bkg.GetName()," ",h_cr_bkg.Integral())

  # create roodatahist of the background histogram in CR.
  dh_cr_bkg = rt.RooDataHist ("dh_"+region_proc_cr+anacat_+"_"+year_,"dh_"+region_proc_cr+anacat_+"_"+year_,vars,h_cr_bkg)

  # another copy fo the wjets in wenu CR for division and saving thr TFs central value.
  # transfer factor is defined as ratio of TF =  bkg in CR / bkg in SR

  print(" datahist created ",h_cr_bkg.GetName()," ",h_sr_bkg.GetName()," ",h_cr_bkg.GetNbinsX()," ",h_sr_bkg.GetNbinsX())

  # --- This is the transfer factor used untill now,From 8th Feb 2021 inverted TF are used.
  #TH1F* htf_cr_bkg = (TH1F*) h_cr_bkg.Clone()
  #htf_cr_bkg.Divide(h_sr_bkg)

  # ---  Inverted Transfer factor. later the multiplication is also changed.
  htf_cr_bkg = h_sr_bkg.Clone()
  htf_cr_bkg.Divide(h_cr_bkg)



  # writing this to the root file for presentation purpose.
  h_vec_tf.append(htf_cr_bkg)

  # Get bin content of each bin of this ratio histogram and save it in the RooRealVar which will be used later for the Actual Transfer Factor with effect of Nuisance parameters included
  # idelaly each of these rooreal var in following vector should be setConstat(1) otherwise it may be treated as free parameter however it should be fixed.
  bincontents_htf_cr_bkg =  GetBinContents(htf_cr_bkg)

  tf = {}
  for i in range(len(bincontents_htf_cr_bkg)):
    tf.update({i+1:rt.RooRealVar("tf"+str(i+1)+"_"+region_proc_cr+anacat_+"_"+year_,"tf"+str(i+1)+"_"+region_proc_cr+anacat_+year_,bincontents_htf_cr_bkg[i])})

  # at this moment keeping this code here for add systematics on the TF, considered only two nuisances,will complete the list later on,once i know which other nuisances has to be here at least working template is here,not only string has to be added to the vector to add a new nuisance

  # ------ all the nuisances log N has to be added before creating RooFormulaVar of the Transfer Factors.
  # ------ adding nuisance by hand,magnitue of each bin can be different as in the e.g. below


  tf_stats_err_vector = []
  # updated stats error from root file
  stats_err_hist_name = anacat_orig+"/"+crname+"/"+"allbin"
  print(" ---------------- stats_err_hist_name: ",stats_err_hist_name)
  stats_error_ = fIn_.Get(stats_err_hist_name)
  for i in range(1,nHistbins+1):
    tf_stats_err_vector.append(stats_error_.GetBinContent(i))  ## TO BE CHECKED FOR

  rfv_bin = {}
  syst_counter = 0
  for i in range(nHistbins):
    rfv_bin.update({i+1:"@0*"}) # this is transfer factor  , ++ is needed so that the counter is increamented automatically after its usage
  syst_counter +=1
  rfv_tf_stats_err_vector = createnuisance(tf_stats_err_vector,nHistbins, syst_counter)

  for key in rfv_bin:
    rfv_bin[key]+= rfv_tf_stats_err_vector[key-1]


  print(" stats error added ")

  # allow the stats error to vary fom 0 to  1* sigma
  # to make them gaussian constrained add param line in the datacards otherwise it is not gaussian constrained.
  rrv_stats_err_bin = {}
  ral_bin = {}
  for i in range(1, nHistbins+1):
    rrv_stats_err_bin.update({i:rt.RooRealVar("rrv_CMS"+year_+"_stats_err_"+region_proc_cr+anacat_+"_bin"+str(i),"rrv_stats_err_"+region_proc_cr+"_bin"+str(i),tf_stats_err_vector[i-1], 0.5*tf_stats_err_vector[i-1],2.*tf_stats_err_vector[i-1])})
    ral_bin.update({i:rt.RooArgList()})

  for key in ral_bin:
    ral_bin[key].add(tf[key])
    ral_bin[key].add(rrv_stats_err_bin[key])

  rrv_syst = []

  print(" number of nuisances : ",len(nuisIndex))

  for isys in range(len(nuisIndex)):
    add_logN_systematic = []
    if (nuisIndex[isys]>23 ):
      syst_counter +=1
      add_logN_systematic = createnuisance(nuisanceValue[nuisIndex[isys]],nHistbins,syst_counter)

    if (nuisIndex[isys] <=23 ): # this will take value from the histogram NOT the flat value in vector.
      add_logN_systematic = []
      print("------------------systematic name: ",isys,"  ",nuisIndex[isys]," ",anacat_orig+"/"+crname+"/"+nuisanceName[nuisIndex[isys]])
      btagunc = fIn_.Get(anacat_orig+"/"+crname+"/"+nuisanceName[nuisIndex[isys]])
      btaguncvec = GetBinContents(btagunc)
      syst_counter +=1
      add_logN_systematic = createnuisance(btaguncvec,nHistbins,syst_counter)

    print("rfv_bin", rfv_bin[1])
    for key in rfv_bin:
      rfv_bin[key] += "*"+add_logN_systematic[key-1]

    for key in rfv_bin:
      print(" bin "+str(key)+" stats unc ",rfv_bin[key]," after including ",nuisanceName[nuisIndex[isys]])

    print"rrv_syst ", (nuisanceName[nuisIndex[isys]],"rrv_"+nuisanceName[nuisIndex[isys]],nuisanceValue[nuisIndex[isys]],0.,1.*nuisanceValue[nuisIndex[isys]])
    rrv_syst.append(rt.RooRealVar(nuisanceName[nuisIndex[isys]],"rrv_"+nuisanceName[nuisIndex[isys]],nuisanceValue[nuisIndex[isys]],0.,1.*nuisanceValue[nuisIndex[isys]]))

  for key in ral_bin:
    for rrvsyst in rrv_syst:
      ral_bin[key].add(rrvsyst)


  print("Bins already included in the lists ",ral_bin[1])
  for key in rfv_bin:
    print(" bin "+str(key)+" total unc is ",rfv_bin[key])

  TF = {}


  print("RAL = ",ral_bin[1][0])
  for i in range(1,nHistbins+1):
    TF.update({i:rt.RooFormulaVar("TF"+str(i)+region_proc_cr+anacat_+"_"+year_, "Transfer factor",rfv_bin[i], ral_bin[i])})
  print(" TF done ")

  rfv_cr_bkg = {}
  for i in range(1,nHistbins+1):
    rfv_cr_bkg.update({i:rt.RooFormulaVar("rfv_"+region_proc_cr+str(i)+anacat_+"_"+year_, "Background yield in control region,bin "+str(i), "(1.0/@0)*@1" ,rt.RooArgList(TF[i],rrvbc_sr_bkg.at(i-1)))})



  # --------------------------------------------------------------
  # ------------------------WJets (muon ) Control region ---------
  # --------------------------------------------------------------

  ral_cr_bkg = rt.RooArgList()
  for i in range(1,nHistbins+1):
    ral_cr_bkg.add(rfv_cr_bkg[i])


  rph_cr_bkg = rt.RooParametricHist("rph_"+region_proc_cr+anacat_+"_"+year_,"Background PDF in control region",met,ral_cr_bkg,h_sr_data)
  rph_cr_bkg_norm = rt.RooAddition("rph_"+region_proc_cr+anacat_+"_"+year_+"_norm","Total Number of events from background in control region",ral_cr_bkg)

  getattr(wspace,'import')(rph_cr_bkg)
  getattr(wspace,'import')(rph_cr_bkg_norm,rt.RooFit.RecycleConflictNodes())

  print(" workspace for one CR is imported. ")



def runPrepareWS(model_="monoHbb",analysiscategory_="merged", mode__ = "RECREATE", inputdir=".", inputfile="AllMETHistos.root", year="2016", nbins=4, version = "_V0"):
  anacat_ = analysiscategory_
  outputfile  = model_+"_"+year+"_WS.root"
  cat__ =  analysiscategory_
  debug__ = True
  AnaYearCat  = model_ +  year + "_" + cat__ +"_"
  print(" AnaYearCat = ",AnaYearCat)
  usebkgsum = False
  # Get the binning from histogram which can be used later in the code throughout.
  # Open input file with all the histograms.
  fin = OpenRootFile(inputdir+"/"+inputfile)
  h_binning = fin.Get("bbDM"+year+"_"+anacat_+"_SR_2HDMa_Ma500_MChi1_MA600_tb35_st_0p7")

  bins = []
  met_low = h_binning.GetBinLowEdge(1)
  met_hi  = h_binning.GetBinLowEdge(nbins+1)
  print( "met_low: met_hi: ",met_low," ",met_hi)

  for ibin in range(1,nbins+1):
    bins.append(h_binning.GetBinLowEdge(ibin))

  print("Integral of the histogram is",h_binning.Integral())

  for ibin in range(nbins):
    print(" bins = ",ibin," ",bins[ibin])

  h_vec_tf = []

  # As usual, load the combine library to get access to the RooParametricHist
  rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
  # Output file and workspace
  fOut = OpenRootFile(outputfile, mode__)
  workspacename = "ws_"+model_+"_"+analysiscategory_+"_"+year
  workspacetitle = "work space for year "+year+", analysis "+model_+", category "+analysiscategory_
  wspace = rt.RooWorkspace(workspacename,workspacetitle)
  fitvariable_ = ""
  if (anacat_=="1b"): fitvariable_="met"
  if (anacat_=="2b"): fitvariable_="cts"

  # A search in a MET tail, define MET as our variable
  met = rt.RooRealVar(fitvariable_, fitvariable_ ,met_low, met_hi)
  vars = rt.RooArgList(met)

  print(" debug 2" )

  # this histogram is just for the binning
  # --- commented on 5 Feb to see if the limis becomes same when using the opriginal data histogram
  h_sr_data = fin.Get(AnaYearCat+"SR_bkgSum")
  print( "histogram name binning: ",h_sr_data.GetName()," ",AnaYearCat+"SR_bkgSum")
  #the following lines create a freely floating parameter for each of our bins (in this example, there are only 4 bins, defined for our observable met.
  # In this case we vary the normalisation in each bin of the background from N/3 to 3*N,
  # e.g. if actual content in the histogram is 55 then we initialize
  # it with 55 and vary it from 55/3 to 55*3. which is very close to freely floating. This can be checked if this works for the cases when bin content is very low,
  # specially in the tails and can be changed easily .


  nuisancePostfix = "CMS"+year+"_"
  nuisanceName = {}
  nuisanceValue = {}

  nuisanceName.update({0:nuisancePostfix+"trig_ele"}), nuisanceValue.update({0:0.02})   #  0
  nuisanceName.update({1:nuisancePostfix+"EleRECO"}), nuisanceValue.update({1:0.01})   #  1
  nuisanceName.update({2:nuisancePostfix+"EleID"}), nuisanceValue.update({2:0.07})   #  2

  nuisanceName.update({3:nuisancePostfix+"MuTRK"}), nuisanceValue.update({3:0.03}) # 3
  nuisanceName.update({4:nuisancePostfix+"MuID"}), nuisanceValue.update({4:0.01}) # 4
  nuisanceName.update({5:nuisancePostfix+"MuISO"}), nuisanceValue.update({5:0.01}) # 5

  nuisanceName.update({6:nuisancePostfix+"metTrig"}), nuisanceValue.update({6:0.01}) # 6
  nuisanceName.update({7:nuisancePostfix+"prefire"}), nuisanceValue.update({7:0.01}) # 7
  nuisanceName.update({8:nuisancePostfix+"eff_b"}), nuisanceValue.update({8:0.10}) # 8

  nuisanceName.update({9:"JECAbsolute"}), nuisanceValue.update({9:0.01}) # 9
  nuisanceName.update({10:"JECFlavorQCD"}) , nuisanceValue.update({10:0.01}) # 10
  nuisanceName.update({11:"JECBBEC1"}), nuisanceValue.update({11:0.01}) # 11
  nuisanceName.update({12:"JECRelativeBal"}) , nuisanceValue.update({12:0.01}) # 12

  nuisanceName.update({13:"JECAbsolute_"+year}) , nuisanceValue.update({13:0.01}) # 13
  nuisanceName.update({14:"JECRelativeSample_"+year}) , nuisanceValue.update({14:0.01}) # 14

  nuisanceName.update({15:nuisancePostfix+"pdf"}), nuisanceValue.update({15:0.10}) # 15
  nuisanceName.update({16:nuisancePostfix+"mu_scale_zjets"}), nuisanceValue.update({16:0.10}) # 16

  nuisanceName.update({17:nuisancePostfix + "mu_scale_wjets"}),  nuisanceValue.update({17:0.10})# 17
  nuisanceName.update({18:nuisancePostfix + "mu_scale_tt"}),  nuisanceValue.update({18:0.10})# 18
  nuisanceName.update({19:nuisancePostfix + "mu_scale_singlet"}),   nuisanceValue.update({19:0.10})# 19
  nuisanceName.update({20:nuisancePostfix + "mu_scale_qcd"}),  nuisanceValue.update({20:0.10})# 20
  nuisanceName.update({21:nuisancePostfix + "mu_scale_dyjets"}),  nuisanceValue.update({21:0.10})# 21
  nuisanceName.update({22:nuisancePostfix + "mu_scale_diboson"}),  nuisanceValue.update({22:0.10})# 22
  nuisanceName.update({23:nuisancePostfix + "mu_scale_smh"}),  nuisanceValue.update({23:0.10})# 23


  '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Top mu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  '''

  nuisIndex = []
  if(anacat_=="2b"):
    print(" calling function for Top mu: ",AnaYearCat+"SR_tt")
    h_sr_top = fin.Get(AnaYearCat+"SR_tt")
    # Get the top hostogram in the Top mu CR
    h_topmu_2b_top = fin.Get(AnaYearCat+"TOPMU_tt")


    # Create all the inputs needed for this CR
    # list of systematics for Top mu CR
    if (year=="2016"):
      nuisIndex.append(3)
      nuisIndex.append(7)


    nuisIndex.append(4)
    nuisIndex.append(5)

    #JECs  9-14
    nuisIndex.append(9)
    nuisIndex.append(10)
    nuisIndex.append(11)
    nuisIndex.append(12)
    nuisIndex.append(13)
    nuisIndex.append(14)
    nuisIndex.append(15)
    nuisIndex.append(16)

    if (year=="2017"):
      nuisIndex.append(7)

    # mu efficiency for Top mu CR
    createRegion(h_vec_tf,met, h_sr_top, h_topmu_2b_top, h_sr_data, wspace, "TOPMU_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_,year,fin,"TOPMU")

    '''
      -------------------------------------------------------------------------------------------------------------------
      ---------------------------------------------- Top e CR -----------------------------------------------------------
      -------------------------------------------------------------------------------------------------------------------
    '''
    nuisIndex = []
    nuisIndex.append(0)
    nuisIndex.append(1)
    nuisIndex.append(2)
    #nuisIndex.push_back(6)
    if (year=="2017"): nuisIndex.append(7)
    if (year=="2016"): nuisIndex.append(7)
    #JECs  9-14
    nuisIndex.append(9)
    nuisIndex.append(10)
    nuisIndex.append(11)
    nuisIndex.append(12)
    nuisIndex.append(13)
    nuisIndex.append(14)
    nuisIndex.append(15)
    nuisIndex.append(16)


    print(" calling function for Top e")
    # Get the top hostogram in the Top mu CR
    h_tope_2b_top = fin.Get(AnaYearCat+"TOPE_tt")
    # Create all the inputs needed for this CR
    createRegion(h_vec_tf,met, h_sr_top, h_tope_2b_top, h_sr_data, wspace, "TOPE_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue,anacat_,year,fin,"TOPE")
   ##/ if(anacat_=="2b")

  '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W enu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
   '''


  print(" anacat_: ",(anacat_=="1b"))
  nuisIndex = []
  if (anacat_=="1b"):
    nuisIndex.append(0)
    nuisIndex.append(1)
    nuisIndex.append(2)
    #nuisIndex.push_back(6)

    if (year=="2016"): nuisIndex.append(7)
    if (year=="2017"): nuisIndex.append(7)

    #JECs  9-14
    nuisIndex.append(9)
    nuisIndex.append(10)
    nuisIndex.append(11)
    nuisIndex.append(12)
    nuisIndex.append(13)
    nuisIndex.append(14)
    nuisIndex.append(15)
    nuisIndex.append(16)


    print(" calling function for Wenu",len(nuisIndex))
    # Get the wjets histogram in signal region
    h_sr_wjets = fin.Get(AnaYearCat+"SR_wjets")

    # Get the wjets hostogram in the Wenu CR
    h_wenu_1b_wjets = fin.Get(AnaYearCat+"WE_wjets")

    print(" integral of wenu : ",h_sr_wjets.Integral() ,"  ",h_wenu_1b_wjets.Integral())
    # Create all the inputs needed for this CR
    createRegion(h_vec_tf,met, h_sr_wjets, h_wenu_1b_wjets, h_sr_data, wspace, "WE_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WE")

    #  fixme, creating new for cross-transfer factors
    # ttbar in SR linked to top in W+Jets
    #TH1F* h_wenu_2b_top = (TH1F*) fin.Get(AnaYearCat+"WE_tt")
    #createRegion(met, h_sr_top, h_wenu_2b_top, h_sr_data, wspace, "WE_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WE")

    '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- W munu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
    '''


    nuisIndex = []
    if (year=="2016"):
      nuisIndex.append(3)
      nuisIndex.append(7)
    nuisIndex.append(4)
    nuisIndex.append(5)
    if (year=="2017"): nuisIndex.append(7)

    #JECs  9-14
    nuisIndex.append(9)
    nuisIndex.append(10)
    nuisIndex.append(11)
    nuisIndex.append(12)
    nuisIndex.append(13)
    nuisIndex.append(14)
    #nuisIndex.append(15)
    #nuisIndex.append(16)

    print(" calling function for Wmunu")
    # Get the wjets hostogram in the Wmunu CR
    h_wmunu_1b_wjets = fin.Get(AnaYearCat+"WMU_wjets")
    # Create all the inputs needed for this CR
    createRegion(h_vec_tf, met, h_sr_wjets, h_wmunu_1b_wjets, h_sr_data, wspace, "WMU_wjets", "SR_wjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"WMU")

    #  fixme, creating new for cross-transfer factors
    # ttbar in SR linked to top in W+Jets
    #TH1F* h_wmunu_2b_top = (TH1F*) fin.Get(AnaYearCat+"WMU_tt")
    #createRegion(met, h_sr_top, h_wmunu_2b_top, h_sr_data, wspace, "WMU_tt", "SR_tt",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,WMU)
  '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zmumu CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  '''

  nuisIndex = []
  if (year=="2016"):
    nuisIndex.append(3)
    nuisIndex.append(7)
  nuisIndex.append(4)
  nuisIndex.append(5)
  if (year=="2017"): nuisIndex.append(7)
  nuisIndex.append(8)

  #JECs  9-14
  nuisIndex.append(9)
  nuisIndex.append(10)
  nuisIndex.append(11)
  nuisIndex.append(12)
  nuisIndex.append(13)
  nuisIndex.append(14)
  nuisIndex.append(15)
  nuisIndex.append(16)



  print(" calling function for Zmumu")
  h_sr_Z = fin.Get(AnaYearCat+"SR_zjets")
  # Get the top hostogram in the Top mu CR
  h_Zmumu_2b_Z = fin.Get(AnaYearCat+"ZMUMU_dyjets")
  # Create all the inputs needed for this CR
  createRegion(h_vec_tf, met, h_sr_Z, h_Zmumu_2b_Z, h_sr_data, wspace, "ZMUMU_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"ZMUMU")


  '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Zee CR -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  '''

  nuisIndex = []
  nuisIndex.append(0)
  nuisIndex.append(1)
  nuisIndex.append(2)
  #nuisIndex.push_back(6)
  if (year=="2016"): nuisIndex.append(7)
  if (year=="2017"): nuisIndex.append(7)

  nuisIndex.append(8)


  #JECs  9-14
  nuisIndex.append(9)
  nuisIndex.append(10)
  nuisIndex.append(11)
  nuisIndex.append(12)
  nuisIndex.append(13)
  nuisIndex.append(14)
  nuisIndex.append(15)
  nuisIndex.append(16)



  # Get the top hostogram in the Top mu CR
  h_Zee_2b_Z = fin.Get(AnaYearCat+"ZEE_dyjets")
  # Create all the inputs needed for this CR
  createRegion(h_vec_tf, met, h_sr_Z, h_Zee_2b_Z, h_sr_data, wspace, "ZEE_dyjets", "SR_zjets",  fOut, nuisIndex, nuisanceName, nuisanceValue, anacat_, year,fin,"ZEE")

  print(" all crs done ")


  #} # end of the debug__
  '''
    -------------------------------------------------------------------------------------------------------------------
    ---------------------------------------------- Signal -----------------------------------------------------------
    -------------------------------------------------------------------------------------------------------------------
  '''

  nuisancesName = []
  nuisancesName.append("")

  nuisList = ['CMS'+year+'_PU','CMS'+year+'_eff_b','CMS'+year+'_fake_b', 'CMS'+year+'_trig_met', 'CMS'+year+'_trig_ele', 'CMS'+year+'_EleID', 'CMS'+year+'_EleRECO', 'CMS'+year+'_MuID', 'CMS'+year+'_MuISO', 'CMS'+year+'_MuTRK','CMS'+year+'_prefire', 'JECAbsolute', 'JECAbsolute_'+year, 'JECBBEC1', 'JECBBEC1_'+year, 'JECEC2', 'JECEC2_'+year, 'JECFlavorQCD', 'JECHF', 'JECHF_'+year, 'JECRelativeBal', 'JECRelativeSample_'+year,'CMS'+year+'_mu_scale_zjets','CMS'+year+'_mu_scale_wjets','CMS'+year+'_mu_scale_tt','CMS'+year+'_mu_scale_singlet','CMS'+year+'_mu_scale_qcd','CMS'+year+'_mu_scale_dyjets','CMS'+year+'_mu_scale_diboson','CMS'+year+'_mu_scale_smh','CMS'+year+'_mu_scale_signal','CMS'+year+'_mu_scale_misc','CMS'+year+'_pdf']

  for lst in nuisList:
    nuisancesName.append(lst+"Up") # ups
    nuisancesName.append(lst+"Down")  # down

  for i in range(1,nbins+1):
    nuisancesName.append("stat_bin"+str(i)+"Up")
    nuisancesName.append("stat_bin"+str(i)+"Down")


  #-------------------------------------------------#
  # --------- ADD 2HDM+a signal shapes -------------#
  #-------------------------------------------------#
  signalpoint = []
  if (year!="2016"):
    #signalpoint.push_back(10)
    signalpoint.append(450)


  if (year=="2017" or year == "2018" or year == "2016"):
    signalpoint.append(10)
    signalpoint.append(50)
    signalpoint.append(100)
    signalpoint.append(150)
    signalpoint.append(200)
    signalpoint.append(250)
    signalpoint.append(300)
    signalpoint.append(350)
    signalpoint.append(400)
    signalpoint.append(500)


  mApoint = [600]
  #mApoint.push_back(1200.)


  nsig = len(signalpoint)

  for inuis in range(len(nuisancesName)):
    for is_ in range(nsig):
      for imA in range(len(mApoint)):
        if (year == "2016"):
          if (mApoint[imA] == 1200): continue
          if ((signalpoint[is_] == 100) and (mApoint[imA] == 1200)): continue
          if ((signalpoint[is_] == 300) and (mApoint[imA] == 1200)): continue
        signalname = AnaYearCat + "SR_2HDMa_Ma" + str(signalpoint[is_]) + "_MChi1_MA" + str(mApoint[imA]) + "_tb35_st_0p7"
        if (nuisancesName[inuis] != ""): signalname = signalname + "_" + nuisancesName[inuis]
        if bool(fin.Get(signalname)) == 0:
          print(" histogram : ", signalname, " does not exist")
        if bool(fin.Get(signalname)) != 0:
          print(" histogram : ", signalname, " exist and saving ")
          addTemplate(wspace, vars, fin.Get(signalname))
        print(" ........ saved")


  if (not usebkgsum):
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"SR_data_obs" ) )
    #addTemplate(wspace, vars, (TH1F*) fin.Get(AnaYearCat+"SR_bkgSum") , AnaYearCat+"SR_data_obs" )
    if (anacat_=="2b"):
      addTemplate(wspace, vars, fin.Get(AnaYearCat+"TOPE_data_obs" ) )
      addTemplate(wspace, vars, fin.Get(AnaYearCat+"TOPMU_data_obs" ) )

    if (anacat_=="1b"):
      addTemplate(wspace, vars, fin.Get(AnaYearCat+"WE_data_obs" ) )
      addTemplate(wspace, vars, fin.Get(AnaYearCat+"WMU_data_obs" ) )

    addTemplate(wspace, vars, fin.Get(AnaYearCat+"ZEE_data_obs" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"ZMUMU_data_obs" ) )


  if (usebkgsum):
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"SR_data_obs" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"TOPE_bkgSum" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"TOPMU_bkgSum" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"WE_bkgSum" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"WMU_bkgSum" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"ZEE_bkgSum" ) )
    addTemplate(wspace, vars, fin.Get(AnaYearCat+"ZMUMU_bkgSum" ) )



 # all other histograms
  regions = []
  regions.append("SR")
  if anacat_=="2b":
    regions.append("TOPE")
    regions.append("TOPMU")
  else:
    regions.append("WE")
    regions.append("WMU")
  regions.append("ZEE")
  regions.append("ZMUMU")

  process = []
  process.append("diboson")
  process.append("gjets")
  process.append("qcd")
  process.append("zjets")
  process.append("smh")
  process.append("wjets")
  process.append("dyjets")
  process.append("tt")
  process.append("singlet")


  category = []
  category.append(AnaYearCat)

  tempname = ""
  outhistnamestat=""
  for inuis in range(len(nuisancesName)):
    for ir in range(len(regions)):
      for ip in range(len(process)):
        for ic in range(len(category)):
          tempname = category[ic] + regions[ir] + "_" + process[ip]
          if (nuisancesName[inuis] != ""):
            tempname = tempname + "_" + nuisancesName[inuis]
            outhistnamestat = tempname
            if ("stat_" in nuisancesName[inuis]):
              outhistnamestat = outhistnamestat.partition(nuisancesName[inuis])[0]+"CMS" + year + "_" + anacat_ + "_" + regions[ir] + "_" + process[ip] + "_"+nuisancesName[inuis]
          if bool(fin.Get(tempname)) == 0:
            print(" histogram : ", tempname, " does not exist")
          if bool(fin.Get(tempname)) != 0:
            print(" histogram : ", tempname, " exist and saving ", outhistnamestat)
            addTemplate(wspace, vars, fin.Get(tempname), outhistnamestat)
          print(" ........ saved")


  # write the workspace at the very end, once everthing has been imported to the workspace
  fOut.cd()
  wspace.Write()
  dirname_ = "transferfactor_" + model_ +"_"  +year + "_" + cat__
  fOut.mkdir(dirname_)
  fOut.cd(dirname_)
  for i in range(len(h_vec_tf)): h_vec_tf[i].Write()



#command  python runPrepareWS.py -M bbDM -c merged -m RECREATE -I . -i rootfile -y 2016 -b 4
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)

parser.add_option("-M","--model", type="string", dest="model_", help="monoHbb or bbDM")
parser.add_option("-c", "--cat", type="string", dest="analysiscategory_", help="histogram dir")
parser.add_option("-m", "--mode", type="string", dest="mode__", help="RECREATE or UPDATE")
parser.add_option("-I", "--inDir", type="string",dest="inputdir", help="input dir")
parser.add_option("-i", "--inFile", type="string",dest="inputfile", help="input File")
parser.add_option("-y", "--year", type="string", dest="year", default="2016")
parser.add_option("-b", "--bins", type="int", dest="nbins")
parser.add_option("-v", "--version", type="string", dest="version", help="version of histograms")
(options, args) = parser.parse_args()

if options.model_ == None:
    print('Please provide model name')
    sys.exit()
else:
    model_ = options.model_

if options.analysiscategory_ == None:
    print('Please provide analysiscategory')
    sys.exit()
else:
    analysiscategory_ = options.analysiscategory_

if options.mode__ == None:
    print('Please provide mode')
    sys.exit()
else:
    mode__ = options.mode__

if options.inputdir == None:
    print('Please provide inputdir')
    sys.exit()
else:
    inputdir = options.inputdir

if options.inputfile == None:
    print('Please provide inputfile')
    sys.exit()
else:
    inputfile = options.inputfile

if options.year == None:
    print('Please provide year')
    sys.exit()
else:
    year = options.year

if options.nbins == None:
    print('Please provide nbins')
    sys.exit()
else:
    nbins = options.nbins



runPrepareWS(model_,analysiscategory_, mode__, inputdir, inputfile, year, nbins)

os._exit(0)