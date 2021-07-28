from ROOT import TCanvas, TGraph, TGraphAsymmErrors, TLegend, TLatex, TFile, TTree, TH2D, TGraph2D
import ROOT as root
from array import array
from sys import argv,stdout,exit
from tdrStyle import *
import plotConfig
from glob import glob 
from collections import namedtuple

root.gROOT.SetBatch(1)


import sys, optparse

usage = "usage: %prog [options] "
parser = optparse.OptionParser(usage)

parser.add_option("-t", "--thdm", action="store_true", dest="thdm")
parser.add_option("-b", "--zpb", action="store_true", dest="zpb")

(options, args) = parser.parse_args()




##Color palette
ncontours = 999;
root.TColor.InitializeColors();
stops  = array('d', [x/7. for x in xrange(8)])
stops  = array('d', [0, 0.25, 0.4, 0.47, 0.54, 0.6, 0.75, 1.0])
reds   = array('d', [ 102./255., 157./255., 188./255., 196./255., 214./255., 223./255., 235./255., 251./255.])
greens = array('d', [  29./255.,  25./255.,  37./255.,  67./255.,  91./255., 132./255., 185./255., 251./255.])
blues  = array('d', [  32./255.,  33./255.,  45./255.,  66./255.,  98./255., 137./255., 187./255., 251./255.])
for a in [reds, greens, blues]:
  a.reverse()
Idx = root.TColor.CreateGradientColorTable(len(stops), stops, reds, greens, blues, 255);
root.gStyle.SetNumberContours(ncontours);
root.gStyle.SetLabelSize(0.035,"X");
root.gStyle.SetLabelSize(0.035,"Y");
root.gStyle.SetLabelSize(0.035,"Z");


setTDRStyle()

XSECUNCERT=0.1
VERBOSE=False

drawLegend=True

iC=0

def get_contours(h2, cold):
  ctmp = TCanvas()
  ctmp.cd()
  h2.Draw("contlist")
  ctmp.Update()

  conts = root.gROOT.GetListOfSpecials().FindObject("contours")
  graphs = []
  for ib in xrange(conts.GetSize()):
    l = conts.At(ib)
    #graph = root.TGraph(l.First())
    graph = l.First()
    if not graph:
      continue
    graph = root.TGraph(graph) # clone
    graph.SetLineColor(h2.GetLineColor())
    graph.SetLineWidth(h2.GetLineWidth())
    graph.SetLineStyle(h2.GetLineStyle())
    graphs.append(graph)

  cold.cd()
  return graphs

L = namedtuple('L', ['mMed','mChi','down2','down1','cent','up1','up2','obs'])

def parseLimitFiles2D(filepath):
  # returns a dict (mMed,mChi) : Limit
  # if xsecs=None, Limit will have absolute xsec
  # if xsecs=dict of xsecs, Limit will have mu values
  limits = {}
  flist = list(open(filepath, 'r').readlines())
  for line in flist[1:]:
    l = L(*map(float, line.strip().split()))
    limits[(l.mMed , l.mChi)] = l
  print 'Successfully parsed %i points'%(len(limits))
  return limits

def makePlot2D(filepath,foutname,medcfg,chicfg,header='',offshell=False):
  limits = parseLimitFiles2D(filepath)
  gs = {}
  for g in ['exp','expup','expdown','obs','obsup','obsdown']:
    gs[g] = TGraph2D()

  iP=0
  hgrid = TH2D('grid','grid',medcfg[0],medcfg[1],medcfg[2],chicfg[0],chicfg[1],chicfg[2])
  for p in limits:
    mMed = p[0]; mChi = p[1]
    l = limits[p]
    if l.obs==0 or l.cent==0:
      print mMed,mChi
      continue
    hgrid.Fill(mMed,mChi,100)
    gs['exp'].SetPoint(iP,mMed,mChi,l.cent)
    gs['expup'].SetPoint(iP,mMed,mChi,l.up1)
    gs['expdown'].SetPoint(iP,mMed,mChi,l.down1)
    gs['obs'].SetPoint(iP,mMed,mChi,l.obs)
    gs['obsup'].SetPoint(iP,mMed,mChi,l.obs/(1-XSECUNCERT))
    gs['obsdown'].SetPoint(iP,mMed,mChi,l.obs/(1+XSECUNCERT))
    iP += 1

  hs = {}
  for h in ['exp','expup','expdown','obs','obsup','obsdown']:
    hs[h] = TH2D(h,h,medcfg[0],medcfg[1],medcfg[2],chicfg[0],chicfg[1],chicfg[2])
    # hs[h].SetStats(0); hs[h].SetTitle('')
    for iX in xrange(0,medcfg[0]):
      for iY in xrange(0,chicfg[0]):
        x = medcfg[1] + (medcfg[2]-medcfg[1])*iX/medcfg[0]
        y = chicfg[1] + (chicfg[2]-chicfg[1])*iY/chicfg[0]
        if not(offshell) and 2*y>x:
          val = 9999
        else:
          val = gs[h].Interpolate(x,y)
        if val == 0:
          val = 9999
        val = max(0.01,min(100,val))
        hs[h].SetBinContent(iX+1,iY+1,val)


  hs['obsclone'] = hs['obs'].Clone() # clone it so we can draw with different settings
  for h in ['exp','expup','expdown','obsclone','obsup','obsdown']:
    hs[h].SetContour(2)
    hs[h].SetContourLevel(1,1)
    for iX in xrange(1,medcfg[0]+1):
      for iY in xrange(1,chicfg[0]+1):
        if hs[h].GetBinContent(iX,iY)<=0:
          hs[h].SetBinContent(iX,iY,100)

  


  global iC
  canvas = ROOT.TCanvas("canvas%i"%iC, '',  1000, 800)
  canvas.SetLogz()
  iC+=1

  frame = canvas.DrawFrame(medcfg[1],chicfg[1],medcfg[2],chicfg[2],"")

  frame.GetYaxis().CenterTitle();
  #frame.GetYaxis().SetTitle("m_{A} [TeV]");
  if options.thdm: frame.GetYaxis().SetTitle("m_{A} (TeV/c^{2})");
  if options.zpb:  frame.GetYaxis().SetTitle("m_{#chi} (TeV/c^{2})");
  frame.GetXaxis().SetTitle("m_{Z'} (TeV/c^{2})");
  frame.GetXaxis().SetTitleOffset(1.15);
  frame.GetYaxis().SetTitleOffset(1.15);
#  frame.GetXaxis().SetNdivisions(5)

  frame.Draw()

  htest = hs['exp']

  obs_color = root.kOrange

  hs['obs'].SetMinimum(0.01)
  hs['obs'].SetMaximum(100.)

  hs['obs'].Draw("COLZ SAME")

  hs['obsclone'].SetLineStyle(1)
  hs['obsclone'].SetLineWidth(3)
  hs['obsclone'].SetLineColor(obs_color)
  hs['obsclone'].Draw('CONT3 SAME')

  ctemp = root.TCanvas()
  hs['obsclone'].Draw('contlist')
  ctemp.Update()
  objs = root.gROOT.GetListOfSpecials().FindObject('contours')
  saveobs = root.TGraph((objs.At(0)).First())

  canvas.cd()

  root.gStyle.SetLineStyleString(11, '40 80')

  conts = {}

  hs['obsup'].SetLineStyle(3)
  hs['obsup'].SetLineWidth(2)
  hs['obsup'].SetLineColor(obs_color)
  conts['obsup'] = get_contours(hs['obsup'], canvas)[0]
  conts['obsup'].Draw('L SAME')
#  hs['obsup'].Draw('CONT3 SAME')

  hs['obsdown'].SetLineStyle(3)
  hs['obsdown'].SetLineWidth(2)
  hs['obsdown'].SetLineColor(obs_color)
  conts['obsdown'] = get_contours(hs['obsdown'], canvas)[0]
  conts['obsdown'].Draw('L SAME')
  #hs['obsdown'].Draw('CONT3 SAME')

  hs['exp'].SetLineStyle(1)
  hs['exp'].SetLineWidth(3)
  hs['exp'].SetLineColor(1)
  hs['exp'].Draw('CONT3 SAME')
  
  conts['exp'] = get_contours(hs['exp'], canvas)[0]
  conts['obsclone'] = get_contours(hs['obsclone'], canvas)[0]


  hs['expup'].SetLineStyle(3)
  hs['expup'].SetLineWidth(2)
  hs['expup'].SetLineColor(1)
  conts['expup'] = get_contours(hs['expup'], canvas)[0]
  conts['expup'].Draw('L SAME')
  #hs['expup'].Draw('CONT3 SAME')

  hs['expdown'].SetLineStyle(3)
  hs['expdown'].SetLineWidth(2)
  hs['expdown'].SetLineColor(1)
  conts['expdown'] = get_contours(hs['expdown'], canvas)[0]
  conts['expdown'].Draw('L SAME')
  #hs['expdown'].Draw('CONT3 SAME')


  #graphroot = TFile("limitGraphsZpBCombo_bb_gg_WW_tt.root","RECREATE")
  graphroot = TFile("limitGraphsZpBCombo_bb_fromLaptop.root","RECREATE")
  graphroot.cd()
  h_exp = conts['exp']
  h_exp.SetName("expected_curve")
  h_exp.Write()  
  #conts['exp'].Write()
  
  conts['expup'].Write()
  conts['expdown'].Write()
  #conts['obsclone'].Write()
  
  h_obs = conts['obsclone']
  h_obs.SetName("observed_curve")
  h_obs.Write()
  
  conts['obsup'].Write()
  conts['obsdown'].Write()

  



  if drawLegend:
    leg = root.TLegend(0.13,0.75,0.39,0.9);#,NULL,"brNDC");
    leg.SetHeader(header)
    leg.AddEntry(hs['exp'],"Median expected 95% CL","L");
    leg.AddEntry(hs['expup'],"Exp. #pm 1 #sigma_{experiment}","L");
    leg.AddEntry(hs['obsclone'],"Observed 95% CL","L");
    leg.AddEntry(hs['obsup'],"Obs. #pm 1 #sigma_{theory}","L");
    leg.SetFillColor(0); leg.SetBorderSize(0)
    leg.Draw("SAME");

  tex = root.TLatex();
  tex.SetNDC();
  tex.SetTextFont(42);
  tex.SetLineWidth(2);
  tex.SetTextSize(0.040);
  tex.Draw();
  tex.DrawLatex(0.65,0.94,"35.9 fb^{-1} (13 TeV)");

  coupling = root.TLatex();
  coupling.SetNDC();
  coupling.SetTextFont(42);
  coupling.SetLineWidth(2);
  coupling.SetTextSize(0.025);
  coupling.SetTextColor(0);
  coupling.Draw();
  if options.thdm: 
    coupling.DrawLatex(0.15,0.70,"g_{Z'} = 0.8, g_{#chi} = 1");
    coupling.DrawLatex(0.15,0.65,"m_{#chi} = 100 GeV, tan#beta = 1");
  
  if options.zpb: coupling.DrawLatex(0.15,0.70,"g_{q} = 0.25, g_{#chi} = 1");



  tex2 = root.TLatex();
  tex2.SetNDC();
  tex2.SetTextFont(42);
  tex2.SetLineWidth(2);
  tex2.SetTextSize(0.04);
  tex2.SetTextAngle(90);
  tex2.SetTextAlign(33)
  tex2.DrawLatex(0.965,0.93,"Observed #sigma_{95% CL}/#sigma_{theory}");

  texCMS = root.TLatex(0.12,0.94,"#bf{CMS}");
  texCMS.SetNDC();
  texCMS.SetTextFont(42);
  texCMS.SetLineWidth(2);
  texCMS.SetTextSize(0.05); texCMS.Draw();

  root.gPad.SetRightMargin(0.15);
  root.gPad.SetTopMargin(0.07);
  root.gPad.SetBottomMargin(0.15);
  root.gPad.RedrawAxis();
  root.gPad.Modified(); 
  root.gPad.Update();

  canvas.SaveAs(foutname+'.png')
  canvas.SaveAs(foutname+'.pdf')
  
  texPrelim = root.TLatex(0.2,0.94,"");
  texPrelim.SetNDC();
  texPrelim.SetTextFont(42);
  texPrelim.SetLineWidth(2);
  texPrelim.SetTextSize(0.05); texPrelim.Draw();

  canvas.SaveAs(foutname+'_prelim.png')
  canvas.SaveAs(foutname+'_prelim.pdf')
  
  canvas.SetGrid()

  hgrid.Draw('BOX')
  hs['obsup'].Draw('CONT3 SAME')

  hs['obsdown'].Draw('CONT3 SAME')

  hs['exp'].Draw('CONT3 SAME')

  hs['expup'].Draw('CONT3 SAME')

  hs['expdown'].Draw('CONT3 SAME')

  canvas.SaveAs(foutname+'_grid.png')
  canvas.SaveAs(foutname+'_grid.pdf')

  fsave = root.TFile(foutname+'.root','RECREATE')
  fsave.WriteTObject(hs['obs'],'hobserved')
  fsave.WriteTObject(gs['obs'],'gobserved')
  fsave.WriteTObject(hs['exp'],'hexp')
  fsave.WriteTObject(gs['exp'],'gexp')
  fsave.WriteTObject(saveobs,'observed')
  fsave.Close()
#  canvas.SaveAs(foutname+'.C')

plotsdir = plotConfig.plotDir

#makePlot2D('refined_limits.txt',plotsdir+'/test',(100,0.011,2.0),(100,0.0011,0.7),'Test',True)

#''' for monoh bb '''
#makePlot2D('limits_barzp_cleaned_NoDuplicate.txt',plotsdir+'/test',(100,0.011,2.0),(100,0.0011,0.7),"Z'-Baryonic",True)

''' for mono-h combination '''
if options.thdm:
  makePlot2D('bin/limits_2hdm_combo_scaled_cleaned_NoDuplicate.txt',plotsdir+'/limit2d_2hdm_combo_',(200,0.45,3.5),(100,0.301,1.002),'Z`-2HDM',True)

if options.zpb:
#  makePlot2D('limits_barzp_cleaned_NoDuplicate_CL90_postCWR.txt',plotsdir+'/limit2d_zpb_combo_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
  makePlot2D('limits_barzp_cleaned_NoDuplicate_CL90.txt',plotsdir+'/limit2d_zpb_combo_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)


 #makePlot2D('bin/limits_zpb_combo_cleaned_NoDuplicate_scaled.txt',plotsdir+'/limit2d_zpb_combo_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
  #makePlot2D('limits_barzp_cleaned_NoDuplicate_fromLaptop.txt',plotsdir+'/limit2d_zpb_combo_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
#<<<<<<< HEAD
#  #makePlot2D('/afs/cern.ch/work/k/khurana/public/AnalysisStuff/plotsLimitZpBarApprovalMonoHbb/limits_barzp_monohbb_90C_cleaned_scaled.txt',plotsdir+'/limit2d_zpb_bb_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
#=======
#  makePlot2D('limits_barzp_cleaned_NoDuplicate_CL90.txt',plotsdir+'/limit2d_zpb_combo_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
  makePlot2D('/afs/cern.ch/work/k/khurana/public/AnalysisStuff/plotsLimitZpBarApprovalMonoHbb/limits_barzp_monohbb_90C_cleaned_scaled.txt',plotsdir+'/limit2d_zpb_bb_',(100,0.011*1000,2.0*1000),(100,0.0011*1000,0.7*1000),'Z`-Baryonic',True)
#>>>>>>> 6d7b800b5a2c8f31bc74a296872f8cc35ef5035f

#makePlot2D('/afs/cern.ch/work/k/khurana/monoHSignalProduction/genproductions/bin/MadGraph5_aMCatNLO/testgridpack/CMSSW_7_4_5/src/MonoHCombination/bin/limits_2hdm_combo_xs_scaled.txt',plotsdir+'/test',(100,0.601,3.5),(100,0.301,0.810),'Test',True)
