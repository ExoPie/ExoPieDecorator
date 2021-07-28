#created by Fasya Khuzaimah on 2020.05.14
# changed by Raman Khurana on 2020.09.01

import os, sys
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.append( '-b-' )

from ROOT import TFile, TH1F, TGraph, TGraphAsymmErrors, THStack, TCanvas, TLegend, TPad, gStyle, gPad

import PlotTemplates
from PlotTemplates import *

import array as arr
isgraph = False
year="2016"

inputRootFileName=""
if not isgraph:
    inputRootFileName = "run2_postfit/run2_fitDiagnostics_combined_140fbinv.root"
if  isgraph:
    if year=="2016":
        inputRootFileName = "run2_postfit/fitDiagnostics_combined_2016_data.root"
    if year=="2017":
        inputRootFileName = "run2_postfit/fitDiagnostics_combined_2017_data.root"
    if year=="2018":
        inputRootFileName = "run2_postfit/fitDiagnostics_combined_2018_data.root"

outdir='plots_limit/Stack/'
if isgraph: 
    postfix="_"+year
    
if not isgraph:
    postfix="_run2"

# functions #

def drawenergy():
    pt = TPaveText(0.1577181,0.905,0.9580537,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)
    
    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize *0.7
    pt.SetTextSize(cmstextSize)
    pt.AddText(0.01,0.57,"#font[61]{CMS}")
    
    pt1 = TPaveText(0.1777181,0.905,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)
    pt1.SetTextSize(preliminarytextfize)
    #pt1.AddText(0.155,0.4,"Preliminary")
    pt1.AddText(0.125,0.45," Internal")
    
    pt2 = TPaveText(0.1877181,0.9045,1.1,0.96,"brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)
    if isgraph :
        if year=="2017":
            pt2.AddText(0.53,0.5,"41.5 fb^{-1} (13 TeV)")
        if year=="2016":
            pt2.AddText(0.53,0.5,"36 fb^{-1} (13 TeV)")
        if year=="2018":
            pt2.AddText(0.53,0.5,"59 fb^{-1} (13 TeV)")
    if not isgraph:
        pt2.AddText(0.53,0.5,"139 fb^{-1} (13 TeV)")
    
    return [pt, pt1, pt2]

def myPad():
    c = TCanvas("c", "", 800, 900)
    c.SetTopMargin(0.4)
    c.SetBottomMargin(0.05)
    c.SetRightMargin(0.1)
    c.SetLeftMargin(0.15)
    gStyle.SetOptStat(0)
    
    padMain = TPad("padMain", "", 0.0, 0.25, 1.0, 0.97)
    padMain.SetTopMargin(0.4)
    padMain.SetRightMargin(0.05)
    padMain.SetLeftMargin(0.17)
    padMain.SetBottomMargin(0)
    padMain.SetTopMargin(0.1)
    
    padRatio = TPad("padRatio", "", 0.0, 0.0, 1.0, 0.25)
    padRatio.SetRightMargin(0.05)
    padRatio.SetLeftMargin(0.17)
    padRatio.SetTopMargin(0.0)
    padRatio.SetBottomMargin(0.3)
    padMain.Draw()
    padRatio.Draw()
    
    return [c, padMain, padRatio]

def myLegend(coordinate=[0.48,0.55,0.97,0.87], ncol=1):
    co = coordinate
    leg = TLegend(co[0], co[1], co[2], co[3])
    leg.SetNColumns(ncol)
    leg.SetBorderSize(0)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    return leg

def dataPredRatio(data_, totalBkg_):
    dataPredRatio_ = data_ - totalBkg_
    dataPredRatio_.Divide(totalBkg_)
    return dataPredRatio_

def myStack(fname_, region_, isSR, prefitbackgroundlist_, legendname_, colorlist_, regionName_, dirName_, isMerged, pad1ymax_):
    
    allyields = {"diboson":0.,
                 "qcd":0,
                 "singlet":0.,
                 "smh":0.,
                 "tt":0.,
                 "wjets":0.,
                 "zjets":0.,
                 "dyjets":0.,
                 "data":0.
             }
    
    nbins = 4
    edges = arr.array('f')
    
    openfile = TFile(fname_)
    
    print " "
    print "*************************"
    print region_, "for", dirName_
    print " "
    
    prefit_path = "shapes_prefit/"+region_+"/"
    postfit_path = "shapes_fit_b/"+region_+"/"
    
    
    #get the histograms from prefit directory
    
    print "get histograms from", prefit_path
    print " "
    
    backgroundlist_ = []
    
    for j in prefitbackgroundlist_:
        jh = openfile.Get(postfit_path + j)
        backgroundlist_.append(jh)
        allyields[jh.GetName()] = jh.Integral()
        
    if isSR: signal_ = openfile.Get(postfit_path + "signal")
    
    edges = arr.array('f')
    for i in range(nbins):
        low = backgroundlist_[0].GetXaxis().GetBinLowEdge(i+1)
        edges.append(low)
    up = backgroundlist_[0].GetXaxis().GetBinUpEdge(nbins)
    edges.append(up)

    data = openfile.Get(prefit_path + "data")
    
    if isgraph:
        data_ = TH1F("data_","",nbins,edges)
        nPoints = data.GetN()
        for i in range(nPoints):
            x = ROOT.Double(0)
            y = ROOT.Double(0)
            data.GetPoint(i, x, y)
            k = data_.FindFixBin(x)
            data_.SetBinContent(k, y)
            data_.SetBinError(i+1, data.GetErrorY(i))
    if not isgraph: 
        data_ = data
                

    

    prefit_ = openfile.Get(prefit_path + "total_background")
    
    allyields["data"] = data_.Integral()
    allyields["prefit"] =prefit_.Integral()
    
    print allyields
    #get the histogram from post fit directory

    print "get histograms from", postfit_path
    print " "
    
    postfit_ = openfile.Get(postfit_path + "total_background")




    # draw the histograms #

    leg = myLegend(ncol = 2)
    pad = myPad()
    
    pad[1].cd()
    
    gPad.SetLogy()
    
    data_.SetLineColor(1)
    data_.SetLineWidth(3)
    data_.SetMarkerStyle(20)
    data_.SetMarkerColor(1)
    data_.SetMarkerSize(1.5)
    data_.GetXaxis().SetLabelSize(0)
    data_.GetYaxis().SetLabelSize(0.05)
    data_.GetYaxis().SetTitleOffset(1.2)
    data_.GetYaxis().SetTitleSize(0.05)
    data_.GetYaxis().SetNdivisions(510)
    data_integral  = data_.GetMaximum()
    
    #data_.SetMaximum(pad1ymax_)
    data_.SetMaximum(data_integral*3)
    data_.GetYaxis().SetTitle("Events/GeV")
    data_.Draw("e1")
    
    hs = THStack("hs", "")
    for j in range(len(colorlist_)):
        h = backgroundlist_[j]
        if backgroundlist_[j]:
            print "accessing the histogram for", backgroundlist_[j]
            h.SetFillColor(colorlist_[j])
            h.SetLineColor(colorlist_[j])
            hs.Add(h, "")
            leg.AddEntry(h,legendname_[j],"f")
    hs.Draw("histsame")

    postfit_.SetLineColor(634)
    postfit_.SetMarkerColor(634)
    postfit_.SetLineWidth(4)
    #leg.AddEntry(postfit_, "Post-fit", "l")
    #postfit_.Draw("histsame")
    
    prefit_.Draw("histsame")
    prefit_.SetLineColor(634)
    prefit_.SetMarkerColor(634)
    prefit_.SetLineWidth(3)
    leg.AddEntry(prefit_, "Pre-fit", "l")

    
    if isSR:
        signal_.SetLineColor(416)
        signal_.SetLineWidth(4)
        signal_.SetMarkerStyle(21)
        #signal_.SetMarkerColor(824)
        leg.AddEntry(signal_, "Signal", "l")
        signal_.Draw("histsame")

    leg.AddEntry(data_, "Data", "lep")
    data_.Draw("e1same")

    leg.Draw()

    drawE = drawenergy()
    for i in drawE:
        i.Draw()
    
    pt4 = TPaveText(0.2577181,0.815,0.5580537,0.875,"brNDC")
    pt4.SetBorderSize(0)
    pt4.SetTextAlign(12)
    pt4.SetFillStyle(0)
    pt4.SetTextFont(52)
    pt4.AddText(regionName_)
    pt4.Draw()

    pad[2].cd()

    gPad.GetUymax()

    leg1 = myLegend(coordinate=[0.5,0.80,0.87,0.95])
    leg1.SetTextSize(0.1)

    prefithist = dataPredRatio(data_ = data_, totalBkg_ = prefit_)
    prefithist.SetLineColor(634)
    prefithist.SetMarkerColor(634)
    prefithist.SetLineWidth(3)
    prefithist.SetMarkerSize(1.5)
    prefithist.GetXaxis().SetLabelSize(0.13)
    prefithist.GetXaxis().SetTitleOffset(1)
    prefithist.GetXaxis().SetTitleSize(0.13)
    prefithist.GetXaxis().SetTickLength(0.1)
    prefithist.GetYaxis().SetLabelSize(0.12)
    prefithist.GetYaxis().SetRangeUser(-0.5,0.5)
    prefithist.GetYaxis().SetTitleOffset(0.5)
    prefithist.GetYaxis().SetTitleSize(0.13)
    prefithist.GetYaxis().SetNdivisions(505)
    prefithist.GetYaxis().SetTitle("#frac{Data-Pred}{Pred}")
    prefithist.GetXaxis().SetTitle("Recoil (GeV)")
    leg1.AddEntry(prefithist, "Prefit", "lep")
    prefithist.Draw("e1")

    postfithist = dataPredRatio(data_ = data_, totalBkg_ = postfit_)
    postfithist.SetLineColor(1)
    postfithist.SetLineWidth(3)
    postfithist.SetMarkerSize(1.5)
    postfithist.SetMarkerColor(1)
    postfithist.GetYaxis().SetTitle("#frac{Data-Pred}{Pred}")
    postfithist.GetXaxis().SetTitle("Recoil (GeV)")
    leg1.AddEntry(postfithist, "Postfit", "lep")
    postfithist.Draw("e1same")

    leg1.Draw()

    if not os.path.exists(dirName_):
        os.mkdir(dirName_)

    pad[0].Modified()
    pad[0].Update()
    #    if isMerged:
    pad[0].SaveAs(dirName_+region_+postfix+".pdf")
    pad[0].SaveAs(dirName_+region_+postfix+".png")
    return allyields
#    if not isMerged:
#        pad[0].SaveAs(dirName_+region_+"_resolved_2017.pdf")
#        pad[0].SaveAs(dirName_+region_+"_resolved_2017.png")


#--------------------------------------------------------------------------------#
                            # Finish defining functions #
#--------------------------------------------------------------------------------#





#--------------------------------------------------------------------------------#
## Start of the CR Summary plots 
#--------------------------------------------------------------------------------#



def FillCRSummary(yield_dict_, region_, dirName_, regionName_):
    print "inside FillCRSummary"
    



print "making stack plots"
print " "

regionlist = ["SR", "TOPE", "TOPMU", "WE", "WMU", "ZEE", "ZMUMU"]
regionlist_1b=["cat_1b_"+ir for ir in regionlist]
regionlist_2b=["cat_2b_"+ir for ir in regionlist]
#regionlist = regionlist_1b #+ regionlist_2b

regionName = ["SR", "Top (e)", "Top (#mu)", "W (e)", "W (#mu)", "Z (ee)", "Z (#mu#mu)"]
regionName_1b=[ir+" 1b" for ir in regionName]
regionName_2b=[ir+" 2b" for ir in regionName]
#regionName = regionName_1b #+ regionName_2b
all_yield_dict_1b = {}
all_yield_dict_2b = {}

for i in range(len(regionlist_1b)):
    if (i == 0):
        isSR = True
        prefitbkglist = ["diboson", "qcd", "singlet", "smh", "tt", "wjets", "zjets"]
        legendlist = ["WW/WZ/ZZ", "QCD", "Single t", "SM H", "t#bar{t}", "W(l#nu)+Jets", "Z(ll)+Jets"]
        color = [601, 922, 802, 631, 799, 878, 856]
    if (i == 1) or (i == 2) or (i == 3) or (i == 4):
        isSR = False
        prefitbkglist = ["diboson", "qcd", "singlet", "smh", "tt", "wjets", "dyjets"]
        legendlist = ["WW/WZ/ZZ", "QCD", "Single t", "SM H", "t#bar{t}", "W(l#nu)+Jets", "DY+Jets"]
        color = [601, 922, 802, 631, 799, 878, 417]
    if (i == 5) or (i == 6):
        isSR = False
        prefitbkglist = ["diboson", "singlet", "smh", "tt", "dyjets"]
        legendlist = ["WW/WZ/ZZ", "Single t", "SM H", "t#bar{t}", "DY+Jets"]
        color = [601, 802, 631, 799, 417]

        
    print ("region: ", regionlist_1b[i])
    makeStackMerged = myStack(fname_ = inputRootFileName, region_ = regionlist_1b[i], isSR = isSR, prefitbackgroundlist_ = prefitbkglist, legendname_ = legendlist, colorlist_ = color, regionName_ = regionName_1b[i], dirName_='plots_limit/Stack/', isMerged = True, pad1ymax_ = 100)
    
    all_yield_dict_1b[regionlist_1b[i]]  = makeStackMerged
    
    makeStackResolved = myStack(fname_ = inputRootFileName, region_ = regionlist_2b[i], isSR = isSR, prefitbackgroundlist_ = prefitbkglist, legendname_ = legendlist, colorlist_ = color, regionName_ = regionName_2b[i], dirName_='plots_limit/Stack/', isMerged = False, pad1ymax_ = 1000)
    all_yield_dict_2b[regionlist_2b[i]]  = makeStackResolved



print all_yield_dict_1b
print all_yield_dict_2b

#FillCRSummary(makeStackMerged, region_ = regionlist_1b[i], dirName_='plots_limit/Stack/', regionName_ = regionName_1b[i])

print "copying now.... "
import os
os.system("source copy.sh")
