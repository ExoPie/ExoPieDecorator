# In this at the end of filevector I am putting the dirname
# so loop over n-1 files and n will give the name of the output dir.

# In legend also the n element will give the name for the ratio plot y axis label.
#edited by Monika Mittal 
#Script for ratio plot 
import sys

import ROOT 
ROOT.gROOT.SetBatch(True)
sys.argv.append( '-b-' )


from ROOT import TFile, TH1F, gDirectory, TCanvas, TPad, TProfile,TGraph, TGraphAsymmErrors
from ROOT import TH1D, TH1, TH1I
from ROOT import gStyle
from ROOT import gROOT
from ROOT import TStyle
from ROOT import TLegend
from ROOT import TMath
from ROOT import TPaveText
from ROOT import TLatex

import os
colors=[1,2,4,5,8,9,11,41,46,30,12,28,20,32]
markerStyle=[23,21,22,20,24,25,26,27,28,29,20,21,22,23]            
linestyle=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


def DrawOverlap(fileVec, histVec, titleVec,legendtext,pngname,logstatus=[0,0],xRange=[-99999,99999,1]):

    gStyle.SetOptTitle(0)
    gStyle.SetOptStat(0)
    gStyle.SetTitleOffset(1.1,"Y");
    #gStyle.SetTitleOffset(1.9,"X");
    gStyle.SetLineWidth(3)
    gStyle.SetFrameLineWidth(3); 

    i=0

    histList_=[]
    histList=[]
    histList1=[]
    maximum=[]
    minimum=[]
    
    ## Legend    
    leg = TLegend(0.1, 0.80, 0.89, 0.89)#,NULL,"brNDC");
    leg.SetBorderSize(0)
    leg.SetNColumns(3)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.05)
     
    c = TCanvas("c1", "c1",0,0,500,500)
    c.SetBottomMargin(0.15)
    c.SetLogy(logstatus[1])
    c.SetLogx(logstatus[0])
    print ("you have provided "+str(len(fileVec))+" files and "+str(len(histVec))+" histograms to make a overlapping plot" )
    print "opening rootfiles"
    c.cd()
    
    ii=0    
    inputfile={}
    print str(fileVec[(len(fileVec)-1)])

    for ifile_ in range(len(fileVec)):
        print ("opening file  "+fileVec[ifile_])
        inputfile[ifile_] = TFile( fileVec[ifile_] )
        print "fetching histograms"
        for ihisto_ in range(len(histVec)):
            print ("printing histo "+str(histVec[ihisto_]))
            histo = inputfile[ifile_].Get(histVec[ihisto_])
            #status_ = type(histo) is TGraphAsymmErrors
            histList.append(histo)
            # for ratio plot as they should nt be normalize 
            histList1.append(histo)
            #print histList[ii].Integral()
            #histList[ii].Rebin(xRange[2])
            #histList[ii].Scale(1.0/histList[ii].Integral())
            maximum.append(histList[ii].GetMaximum())
	    minimum.append(histList[ii].GetMinimum())
            maximum.sort()
            ii=ii+1

    print histList
    print maximum, "  ", max(maximum)
    print minimum, "  ", min(minimum)
    for ih in range(len(histList)):
        tt = type(histList[ih])
        if logstatus[1] is 1 :
            histList[ih].SetMaximum(1.5) #1.4 for log
            histList[ih].SetMinimum(0.1) #1.4 for log
        if logstatus[1] is 0 :
            maxi=max(maximum)
	    mini=min(minimum)
	    if maxi==0.0:maxi=0.001
	    if mini==0.0:mini=-0.001
            histList[ih].SetMaximum(maxi*3) #1.4 for log
            histList[ih].SetMinimum(mini*3) #1.4 for log
#        print "graph_status =" ,(tt is TGraphAsymmErrors)
#        print "hist status =", (tt is TH1D) or (tt is TH1F)
        if ih == 0 :      
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("APL")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("P hist")   
        if ih > 0 :
            #histList[ih].SetLineWidth(2)
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("PL same")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("P hist same")   

        if tt is TGraphAsymmErrors :
            histList[ih].SetMaximum(100) 
            histList[ih].SetMarkerColor(colors[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetLineWidth(2)
            histList[ih].SetMarkerStyle(markerStyle[ih])
            histList[ih].SetMarkerSize(1)
            leg.AddEntry(histList[ih],legendtext[ih],"PL")
        if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
            histList[ih].SetLineStyle(linestyle[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetMarkerColor(colors[ih])
            histList[ih].SetMarkerStyle(20)
            histList[ih].SetMarkerSize(1.0)
            histList[ih].SetLineWidth(3)
            leg.AddEntry(histList[ih],legendtext[ih],"P")
        histList[ih].GetYaxis().SetTitle(titleVec[1])
        histList[ih].GetYaxis().SetTitleSize(0.052)
        histList[ih].GetYaxis().SetTitleOffset(0.98)
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
    pt.Draw()
   
    

    leg.Draw()
    outputdirname = 'UncPlots/'
    histname=outputdirname+pngname 
    c.SaveAs(histname+'.png')
    c.SaveAs(histname+'.pdf')
    # outputname = 'cp  -r '+ outputdirname+'/*' +' /afs/cern.ch/work/k/khurana/public/AnalysisStuff/monoH/LimitModelPlots/plots_limit/limitcomp/'
#    os.system(outputname) 
    


print "calling the plotter"

files = ['bin/TF.root']
SR_BKG = ['SR_zjets','SR_zjets','SR_wjets','SR_wjets','SR_tt','SR_tt']
CR_BKG = ['ZEE_dyjets','ZMUMU_dyjets','WE_wjets','WMU_wjets','TOPE_tt','TOPMU_tt']  #PLEASE MAKE SURE YOU GIVE PROCESS NAME IN AN ORDER AS SR
#postfix= ['allbinUp','JECUp','PrefireUp']
postfix=["allbin","EleTrig","EleID","EleRECO","MuID","MuTRK"] #PROVIDE SYS HISTS WITH UP OR DOWN 
xtitle='Recoil [GeV]'
ytitle='relative unc'
axistitle = [xtitle, ytitle]

cats   = ['1b','2b']
for cat in cats:
    for pf in postfix:
        for sr_bkg, cr_bkg in zip(SR_BKG,CR_BKG):
            	
	    uphist  = "Unc_tf_"+cat+"_"+sr_bkg+"_to_"+cat+"_"+cr_bkg+"_"+pf+"Up"
	    downhist="Unc_tf_"+cat+"_"+sr_bkg+"_to_"+cat+"_"+cr_bkg+"_"+pf+"Down"
            if ("ZEE" in uphist or "WE" in uphist or "TOPE" in uphist) and "Mu" in uphist:continue
            if ("ZMUMU" in uphist or "WMU" in uphist or "TOPMU" in uphist) and "Ele" in uphist:continue
	    #f=ROOT.Open(files[0],"READ")
 	    #if not "MuID" in uphist:continue
	    hists = [uphist,downhist]
	    print ("hists",uphist,"  ",downhist)

	    pngname = uphist.replace("Up","")
	    legend  = [pf+"Up",pf+"Down"]

	    DrawOverlap(files,hists,axistitle,legend,pngname,[0,0],[200,1000])
