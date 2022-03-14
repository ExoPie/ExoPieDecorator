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
colors=[1,4,5,8,2,9,41,46,30,12,28,20,32]
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
    
    ## Legend    
    leg = TLegend(0.1, 0.70, 0.89, 0.89)#,NULL,"brNDC");
    leg.SetBorderSize(0)
    leg.SetNColumns(2)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)
     
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
            maximum.sort()
            ii=ii+1

    print histList
    for ih in range(len(histList)):
        tt = type(histList[ih])
        if logstatus[1] is 1 :
            #histList[ih].SetMaximum(100) #1.4 for log
            #histList[ih].SetMinimum(0.1) #1.4 for log
            histList[ih].SetMaximum(10)
            histList[ih].SetMinimum(0.001)
        if logstatus[1] is 0 :
            histList[ih].SetMaximum(1.4) #1.4 for log
            histList[ih].SetMinimum(0.001) #1.4 for log
#        print "graph_status =" ,(tt is TGraphAsymmErrors)
#        print "hist status =", (tt is TH1D) or (tt is TH1F)
        if ih == 0 :      
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("APL")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw()## removed hist   
        if ih > 0 :
            #histList[ih].SetLineWidth(2)
            if tt is TGraphAsymmErrors : 
                histList[ih].Draw("PL same")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("same")   ## removed hist 

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
            histList[ih].SetLineWidth(3)
            leg.AddEntry(histList[ih],legendtext[ih],"L")
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
    outputdirname = 'plots_limit/limitcomp//'
    histname=outputdirname+pngname 
    c.SaveAs(histname+'.png')
    c.SaveAs(histname+'.pdf')
    outputname = 'cp  -r '+ outputdirname+'/*' +' /afs/cern.ch/work/k/khurana/public/AnalysisStuff/monoH/LimitModelPlots/plots_limit/limitcomp/'
#    os.system(outputname) 
    


print "calling the plotter"

'''
files=['bin/limits_monoH_merged_2018.root', 'bin/limits_monoH_resolved_2018.root', 'bin/limits_monoH_combined_2018.root']
legend=['resolved', 'merged', 'combined']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_B_R_C_2018',[0,1],[200,1700])



files=['bin/limits_monoH_merged_2017.root', 'bin/limits_monoH_resolved_2017.root', 'bin/limits_monoH_combined_2017.root']
legend=['resolved', 'merged', 'combined']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_B_R_C_2017',[0,1],[200,1700])



files=['bin/limits_bbDM_combined_2016_4bin.root', 'bin/limits_bbDM_combined_2016_binv2.root' , 'bin/limits_bbDM_combined_2016_binv3.root']
legend=['4 bins', '5 bins V2', '5 bins V3']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_2016_binOptimisation',[0,1],[10,1000])


files=['bin/limits_bbDM_combined_2017_FixedSignalSamples.root', 'bin/limits_bbDM_2b_2017_MonoHCode.root']
legend=['bb+DM', 'bb+DM with monoH f/w']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_monoH_comparison',[0,1],[10,1000])

'''



##
##dirname='bin/AllMETHistos_v17_12-00-02_nobZCR'
##files=[dirname+'/limits_bbDM_1b_2017.root', dirname+'/limits_bbDM_2b_2017.root', dirname+'/limits_bbDM_combined_2017.root']
##legend=['1b', '2b', 'combined']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2017_MET_comparison',[0,1],[10,1000])
##
##
##
##
##
##dirname='bin/AllMETHistos_v16_12_00_02'
##files=[dirname+'/limits_bbDM_1b_2016.root', dirname+'/limits_bbDM_2b_2016.root', dirname+'/limits_bbDM_combined_2016.root']
##legend=['1b', '2b', 'combined']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2016_comparison',[0,1],[10,1000])
##




##dirname='bin/'
##files=[dirname+'/AllMETHistos_v16_12-00-03_1bMET_2bCTS/limits_bbDM_2hdma_2b_2016.root', dirname+'/AllMETHistos_v17_12-00-03_1bMET_2bCTS/limits_bbDM_2hdma_2b_2017.root', dirname+'/AllMETHistos_v18_12-00-03_1bMET_2bCTS/limits_bbDM_2hdma_2b_2018.root',dirname+'/Run2Combo_2b/limits_bbDM_2hdma_2b_run2.root'] 
##legend=['2016', '2017', '2018','run-2']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2b_2hdma_run2_comparison',[0,1],[10,1000])
##


## 
##dirname='bin/'
##files=[dirname+'/AllMETHistos_v16_12-00-03_1bMET_2bCTS/limits_bbDM_1b_2016.root', dirname+'/AllMETHistos_v17_12-00-03_1bMET_2bCTS/limits_bbDM_1b_2017.root', dirname+'/AllMETHistos_v18_12-00-03_1bMET_2bCTS/limits_bbDM_1b_2018.root',dirname+'/Run2Combo_1b/limits_bbDM_1b_run2.root']
##legend=['2016', '2017', '2018','run-2']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_1b_run2_comparison',[0,1],[10,1000])


##
##dirname='bin/'
##files=[dirname+'/AllMETHistos_v17_12-00-03_phoClean/limits_bbDM_2hdma_2b_2017.root', dirname+'/AllMETHistos_v17_12-00-03_genMCwgt/limits_bbDM_2hdma_2b_2017.root',dirname+'AllMETHistos_v17_12-00-04/limits_bbDM_2hdma_2b_2017.root']
##legend=['2017-pho-clean','2017-old-pho-veto', '2017-pho-clean_bjet_combi']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2b_2017_pho_clean_bjetcombinatorics',[0,1],[10,1000])
##
##
##
##
##
##
##dirname='bin/'
##files=[dirname+'/v17_12-00-04_pfMetCorrPt/limits_bbDM_2hdma_2b_2017.root', dirname+'/AllMETHistos_v17_12-00-04/limits_bbDM_2hdma_2b_2017.root']
##legend=['FV6', 'V5']
##
##histoname1=['expmed']
##
##xtitle='m_{A}[GeV]'
##ytitle='#mu'
##axistitle = [xtitle, ytitle]
##DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2b_2017_v5_vs_v6',[0,1],[10,1000])



dirname='bin/'
files=[dirname+'/AllMETHistos_v16_12-02-01_cl68pdf/limits_bbDM_2hdma_2b_2016.root', 
       dirname+'/AllMETHistos_v17_12-02-01_cl68pdf/limits_bbDM_2hdma_2b_2017.root', 
       dirname+'/AllMETHistos_v18_12-02-01_cl68pdf/limits_bbDM_2hdma_2b_2018.root']
legend=['2016', '2017','2018']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_2b_V16_17_18_12-02-01_cl68pdf',[0,1],[10,1000])





dirname='bin/'
files=[dirname+'/AllMETHistos_v16_12-02-01_cl68pdf/limits_bbDM_2hdma_1b_2016.root', 
       dirname+'/AllMETHistos_v17_12-02-01_cl68pdf/limits_bbDM_2hdma_1b_2017.root', 
       dirname+'/AllMETHistos_v18_12-02-01_cl68pdf/limits_bbDM_2hdma_1b_2018.root']
legend=['2016', '2017','2018']

histoname1=['expmed']

xtitle='m_{A}[GeV]'
ytitle='#mu'
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,'limit_bbDM_1b_V16_17_18_12-02-01_cl68pdf',[0,1],[10,1000])


