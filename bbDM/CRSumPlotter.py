from ROOT import TFile,kBlue,kAzure,kCyan,kGray,kOrange,kOrange,kViolet,kGreen ,kBlack,THStack,TLatex, TGraph, TTree, TH1F,  TCanvas, TChain, TMath, TLorentzVector, AddressOf, gROOT, TNamed, gStyle, TLegend
import os
import glob
from array import array

gStyle.SetFrameLineWidth(3)
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetLegendBorderSize(2)
gStyle.SetFillColor(2)
gStyle.SetLineWidth(1)
c=TCanvas()
c.SetLogy()
labels=['1mu1b','1mu2b','2mu1b','2mu2b','1e1b','1e2b','2e1b','2e2b']#,'1e1mu2b']
#labels=['1hahamu1b','1hohoe1b','1nonomu2b','1e2b','2mu1b','2e1b','2mu2b','2e2b']

legend=TLegend(.43,.59,.87,.89)
legend.SetNColumns(2)
legend.SetTextSize(0.05)
legend.SetBorderSize(0)
leg_entry=['DIBOSON','ZJets','GJets','QCD','STop','TT','WJets','DYJets']

h_DIBOSON=TH1F("h_DIBOSON",'CR Summary plot',len(labels),0,len(labels))
h_ZJets=TH1F("h_ZJets",'CR Summary plot',len(labels),0,len(labels))
h_GJets=TH1F("h_GJets",'CR Summary plot',len(labels),0,len(labels))
h_QCD=TH1F("h_QCD",'CR Summary plot',len(labels),0,len(labels))
h_STop=TH1F("h_STop",'CR Summary plot',len(labels),0,len(labels))
h_TT=TH1F("h_TT",'CR Summary plot',len(labels),0,len(labels))
h_WJets=TH1F("h_WJets",'CR Summary plot',len(labels),0,len(labels))
h_DYJets=TH1F("h_DYJets",'CR Summary plot',len(labels),0,len(labels))
h_data=TH1F("h_data",'CR Summary plot',len(labels),0,len(labels))

myHists=[h_DIBOSON,h_ZJets,h_GJets,h_QCD,h_STop,h_TT,h_WJets,h_DYJets]
colors=[kBlue+2,kAzure+1,kCyan-9,kGray+1,kOrange+1,kOrange-2,kViolet-3,kGreen+2]



path='rootfile/*.root'


latex =  TLatex();
latex.SetNDC();
latex.SetTextSize(0.04);
latex.SetTextAlign(31);
latex.SetTextAlign(11);


files=sorted(glob.glob(path))

for file in files:
    f=TFile.Open(file,'read')
    print(f)
    if 'Mu' in file.split('/')[-1]:
        h_DIBOSON_mu=f.Get('DIBOSON')
        h_ZJets_mu=f.Get('ZJets')
        h_GJets_mu=f.Get('GJets')
        h_QCD_mu=f.Get('QCD')
        h_STop_mu=f.Get('STop')
        h_TT_mu=f.Get('TT')
        h_Wjets_mu=f.Get('WJets')
        h_DYJets_mu=f.Get('DYJets')
        h_mydata=f.Get('data_obs')
        gotHists_mu=[h_DIBOSON_mu,h_ZJets_mu,h_GJets_mu,h_QCD_mu,h_STop_mu,h_TT_mu,h_Wjets_mu,h_DYJets_mu]

        h_data.SetBinContent(1, h_mydata.GetBinContent(1))
        h_data.SetBinContent(2, h_mydata.GetBinContent(2))
        h_data.SetBinContent(3, h_mydata.GetBinContent(3))
        h_data.SetBinContent(4, h_mydata.GetBinContent(4))

        for i in range(len(gotHists_mu)):
                myHists[i].SetBinContent(1, gotHists_mu[i].GetBinContent(1))
                myHists[i].GetXaxis().SetBinLabel(1, labels[0])
                myHists[i].GetXaxis().SetBinLabel(2, labels[1])
                myHists[i].GetXaxis().SetBinLabel(3, labels[2])
                myHists[i].GetXaxis().SetBinLabel(4, labels[3])
                myHists[i].SetBinContent(2, gotHists_mu[i].GetBinContent(2))

                myHists[i].SetBinContent(3, gotHists_mu[i].GetBinContent(3))

                myHists[i].SetBinContent(4, gotHists_mu[i].GetBinContent(4))


    elif 'Ele' in file.split('/')[-1]:
        h_DIBOSON_e=f.Get('DIBOSON')
        h_ZJets_e=f.Get('ZJets')
        h_GJets_e=f.Get('GJets')
        h_QCD_e=f.Get('QCD')
        h_STop_e=f.Get('STop')
        h_TT_e=f.Get('TT')
        h_Wjets_e=f.Get('WJets')
        h_DYJets_e=f.Get('DYJets')
        h_mydata=f.Get('data_obs')
        gotHists_e=[h_DIBOSON_e,h_ZJets_e,h_GJets_e,h_QCD_e,h_STop_e,h_TT_e,h_Wjets_e,h_DYJets_e]
        h_data.SetBinContent(5, h_mydata.GetBinContent(1))
        h_data.SetBinContent(6, h_mydata.GetBinContent(2))
        h_data.SetBinContent(7, h_mydata.GetBinContent(3))
        h_data.SetBinContent(8, h_mydata.GetBinContent(4))

        for i in range(len(gotHists_e)):
            legend.AddEntry(myHists[i],leg_entry[i],"F")
            myHists[i].SetFillColor(colors[i])
            myHists[i].SetMaximum(1000000)
            myHists[i].SetBinContent(5, gotHists_e[i].GetBinContent(1))
            myHists[i].GetXaxis().SetBinLabel(5, labels[4])
            myHists[i].SetBinContent(6, gotHists_e[i].GetBinContent(2))
            myHists[i].GetXaxis().SetBinLabel(6, labels[5])
            myHists[i].SetBinContent(7, gotHists_e[i].GetBinContent(3))
            myHists[i].GetXaxis().SetBinLabel(7, labels[6])
            myHists[i].SetBinContent(8, gotHists_e[i].GetBinContent(4))
            myHists[i].GetXaxis().SetBinLabel(8, labels[7])

        #fill the histograms



hs=THStack('hs','CR Summary ')
for i in myHists:
    hs.Add(i)
hs.SetMaximum(40000)
hs.Draw()
legend.Draw()
latex.DrawLatex(0.18, 0.93, "CR Summary")
h_data.SetStats(0)
h_data.SetLineColor(1)
h_data.SetMarkerColor(kBlack)
h_data.SetMarkerStyle(20)
h_data.SetMarkerSize(1.5)
h_data.Draw('same p e1')
c.SaveAs("CRSummary.pdf")
c.SaveAs("CRSummary.png")
