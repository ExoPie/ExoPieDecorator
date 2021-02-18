import os
import ROOT
from math import sqrt


import sys

import ROOT 
ROOT.gROOT.SetBatch(True)
sys.argv.append( '-b-' )
os.system('mkdir TFplots')
os.system('rm -rf TFplots/*')

from ROOT import TFile, TH1F, gDirectory, TCanvas, TPad, TProfile,TGraph, TGraphAsymmErrors
from ROOT import TH1D, TH1, TH1I,kBlue
from ROOT import gStyle
from ROOT import gROOT
from ROOT import TStyle
from ROOT import TLegend
from ROOT import TMath
from ROOT import TPaveText
from ROOT import TLatex

import os
colors=[kBlue-6,1,4,5,8,9,11,41,46,30,12,28,20,32]
markerStyle=[23,21,22,20,24,25,26,27,28,29,20,21,22,23]            
linestyle=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


def addMultiHistBinErr(f, HISTNAME,HISTNAMELIST):
    hists=[]
    # f=ROOT.TFile.Open(infile)
    mainHist = f.Get(HISTNAME)
    bins = mainHist.GetXaxis().GetNbins()
    for ih in HISTNAMELIST:
        h_temp = f.Get(ih)
	print "checking for hist  ",ih 
	print "integral ", h_temp.Integral()
        # h_temp.Add(mainHist,-1)
        hists.append(h_temp)

    for ibin in range(1,bins+1):
        sumError = 0.0
        for ij in range(len(hists)):
            sumError += (abs(hists[ij].GetBinContent(ibin))-abs(mainHist.GetBinContent(ibin)))**2

        binError = sqrt(sumError)
        mainHist.SetBinError(ibin,binError)

    mainHist.SetName("TF_stats_syst")
    mainHist.SetTitle("TF_stats_syst")

    return mainHist

def addHistBinError(f,hist1,hist2):
    hists=[]
    # f=ROOT.TFile.Open(infile)
    mainHist = f.Get(hist1)
    statsHist = f.Get(hist2)
    # statsHist.Add(mainHist,-1)
    bins = mainHist.GetXaxis().GetNbins()
    for ibin in range(1,bins+1):
        binerror=(abs(statsHist.GetBinContent(ibin))-abs(mainHist.GetBinContent(ibin)))
        mainHist.SetBinError(ibin,abs(binerror))


    mainHist.SetName("TF_stats")
    mainHist.SetTitle("TF_stats")

    return mainHist


'''
this fuction is taken raman's code
'''

def DrawOverlap(histList, titleVec,legendtext,pngname,logstatus=[0,0],xRange=[-99999,99999,1],cat='2b'):

    gStyle.SetOptTitle(0)
    gStyle.SetOptStat(0)
    gStyle.SetTitleOffset(1.1,"Y");
    #gStyle.SetTitleOffset(1.9,"X");
    gStyle.SetLineWidth(3)
    gStyle.SetFrameLineWidth(3); 
    gStyle.SetTickLength(0.0,"x")

    i=0

    # histList_=[]
    # histList=[]
    # histList1=[]
    # maximum=[]
    
    ## Legend    
    leg = TLegend(0.2, 0.80, 0.89, 0.89)#,NULL,"brNDC");
    leg.SetBorderSize(0)
    leg.SetNColumns(3)
    # leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    # leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.05)
     
    c = TCanvas("c1", "c1",0,0,500,500)
    c.SetBottomMargin(0.15)
    c.SetLeftMargin(0.15)
    c.SetLogy(logstatus[1])
    c.SetLogx(logstatus[0])
    # print ("you have provided "+str(len(fileVec))+" files and "+str(len(histVec))+" histograms to make a overlapping plot" )
    # print "opening rootfiles"
    c.cd()
    


    print "provided hists", histList
    for ih in range(len(histList)):
        tt = type(histList[ih])
        if logstatus[1] is 1 :
            histList[ih].SetMaximum(1.5) #1.4 for log
            histList[ih].SetMinimum(0.1) #1.4 for log
        if logstatus[1] is 0 :
            maxi = histList[ih].GetMaximum()
            histList[ih].SetMaximum(maxi*2) #1.4 for log
            histList[ih].SetMinimum(0) #1.4 for log
#        print "graph_status =" ,(tt is TGraphAsymmErrors)
#        print "hist status =", (tt is TH1D) or (tt is TH1F)
        if ih == 0 :      
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("APL")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("PE2 ")   
        if ih > 0 :
            #histList[ih].SetLineWidth(2)
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("PL same")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("PE0  same")   

        if tt is TGraphAsymmErrors :
            histList[ih].SetMaximum(100) 
            histList[ih].SetMarkerColor(colors[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetLineWidth(0)
            histList[ih].SetMarkerStyle(markerStyle[ih])
            histList[ih].SetMarkerSize(1)
            leg.AddEntry(histList[ih],legendtext[ih],"PL")
        if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
            print "setting style for hist"
            print "color code",colors[ih]
            # histList[ih].SetLineStyle(linestyle[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetMarkerColor(colors[ih])
            histList[ih].SetFillColor(colors[ih])
            histList[ih].SetMarkerStyle(20)
            histList[ih].SetMarkerSize(1.0)
            histList[ih].SetLineWidth(1)
            #invert legend between first and second
            if ih==0:leg.AddEntry(histList[ih+1],legendtext[ih+1],"PEL")#"f")
            if ih==1:leg.AddEntry(histList[ih-1],legendtext[ih-1],'f')#"PEL")
        histList[ih].GetYaxis().SetTitle(titleVec[1])
        histList[ih].GetYaxis().SetTitleSize(0.052)
        histList[ih].GetYaxis().SetTitleOffset(1.4)
        histList[ih].GetYaxis().SetTitleFont(42)
        histList[ih].GetYaxis().SetLabelFont(42)
        histList[ih].GetYaxis().SetLabelSize(.052)
        histList[ih].GetXaxis().SetRangeUser(xRange[0],xRange[1])
        #     histList[ih].GetXaxis().SetLabelSize(0.0000);
        
        histList[ih].GetXaxis().SetTitle(titleVec[0])
        histList[ih].GetXaxis().SetLabelSize(0.052)
        histList[ih].GetXaxis().SetTitleSize(0.052)
        #histList[ih].GetXaxis().SetTitleOffset(1.14)
        histList[ih].GetXaxis().SetTitleFont(42)

        histList[ih].GetXaxis().SetLabelFont(42)
        histList[ih].GetYaxis().SetLabelFont(42) 
        histList[ih].GetXaxis().SetNdivisions(507)
        #histList[ih].GetXaxis().SetMoreLogLabels(); 
        #histList[ih].GetXaxis().SetNoExponent();
        #histList[ih].GetTGaxis().SetMaxDigits(3);
        # histList[ih].GetXaxis().SetTickSize(0.00)
        

        i=i+1
    pt = TPaveText(0.01,0.92,0.95,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(42)
    pt.SetTextSize(0.046)
    #text = pt.AddText(0.12,0.35,"CMS Internal                     36 fb^{-1} (2016) ")
    text = pt.AddText(0.12,0.35,"CMS Internal                     41.5 fb^{-1} (2017) ")
    #text = pt.AddText(0.12,0.35,"CMS Internal                     59.6 fb^{-1} (2018) ")
    #text = pt.AddText(0.6,0.5,"41.5 fb^{-1} (2017) ")
    cattxt = TLatex(0.20,0.75,cat+'  '+"category")
    cattxt.SetTextSize(0.06)

    cattxt.SetTextAlign(12)
    cattxt.SetNDC(1)
    cattxt.SetTextFont(42)


    pt.Draw()
    cattxt.Draw()
   
    

    leg.Draw()
    outputdirname = 'TFplots/'
    histname=outputdirname+pngname 
    c.SaveAs(histname+'.png')
    c.SaveAs(histname+'.pdf')
    # outputname = 'cp  -r '+ outputdirname+'/*' +' /afs/cern.ch/work/k/khurana/public/AnalysisStuff/monoH/LimitModelPlots/plots_limit/limitcomp/'
#    os.system(outputname) 
    





def plotTF(infile,SR_BKG,CR_BKG,postfix,cats,yaxisTitle):
    f=ROOT.TFile(infile)
    for cat in cats:
        i=0
        for sr_bkg , cr_bkg in zip(SR_BKG,CR_BKG):
	    
            histname     = "tf_"+cat+"_"+sr_bkg+"_to_"+cat+"_"+cr_bkg
            statsUncHist = histname+"_allbinUp"
            uncHists = []
            for pf in postfix:
                # if 'allbin' in pf:
                #     UncHistname = statsUncHist#"tf_"+cat+"_"+sr_bkg+"_to_"+cat+"_"+cr_bkg+"_"+pf
                #     uncHists.append(UncHistname)
                # else:
                UncHistname = "tf_"+cat+"_"+sr_bkg+"_to_"+cat+"_"+cr_bkg+"_"+pf
		if ("ZEE" in UncHistname or "WE" in UncHistname or "TOPE" in UncHistname) and "Mu" in UncHistname:continue
                if ("ZMUMU" in UncHistname or "WMU" in UncHistname or "TOPMU" in UncHistname) and "Ele" in UncHistname:continue

                uncHists.append(UncHistname)

            '''
            plotting histograms
            '''
            legend = ['TF(stats+syst)','TF(stats)']
            xtitle='Recoil [GeV]'
            ytitle=yaxisTitle[i]
            i+=1
            axistitle = [xtitle, ytitle]
	    print "central histname", histname, "  statsUncHist",statsUncHist
	    print "list of unc hists",uncHists
            TFHist_stats       = addHistBinError(f,histname,statsUncHist)
            TFHist_stats_syst  = addMultiHistBinErr(f,histname,uncHists)

            for i in range(1,5):
                print "error syst stats  ", TFHist_stats_syst.GetBinError(i), "stats  ",TFHist_stats.GetBinError(i),"bin  ",i
            

            histsToOverlay     = [TFHist_stats_syst,TFHist_stats]
            outfileName        = histname
            DrawOverlap(histsToOverlay,axistitle,legend,outfileName,[0,0],[200,1000],cat)



# histname = ("tf_"+sr_bkg+"_to_"+cr_bkg+postfix)
'''
infile='TF.root'
SR_BKG = ['SR_zjets','SR_zjets','SR_wjets','SR_wjets','SR_tt','SR_tt']
CR_BKG = ['ZEE_dyjets','ZMUMU_dyjets','WE_wjets','WMU_wjets','TOPE_tt','TOPMU_tt']  #PLEASE MAKE SURE YOU GIVE PROCESS NAME IN AN ORDER AS SR
postfix= ['allbinUp','JECUp','PrefireUp']
cats   = ['1b','2b']
yaxis  = ['transfer factor (z#nu#nu SR/zee )','transfer factor (z#nu#nu SR/z#mu#mu )',\
        'transfer factor (wl#nu SR/we#nu )','transfer factor (wl#nu SR/w#mu#nu )',\
        'transfer factor (Top SR/Top(e) )','transfer factor (Top SR/Top(#mu) )']
plotTF(infile,SR_BKG,CR_BKG,postfix,cats,yaxis)
'''
