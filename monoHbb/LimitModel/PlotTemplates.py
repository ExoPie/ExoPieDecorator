import ROOT
import os 
import sys 
import time 
import math 
from ROOT import TPaveText, TH2, TLatex, TLegend
from ROOT import TGraph, TFile, TGraphAsymmErrors
from array import array


print "importing finished "
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLineWidth(3)
ROOT.gStyle.SetFrameLineWidth(3); 
ROOT.gStyle.SetPaintTextFormat('4.2f')

#mypalette=[15, 20, 23,30,32]
ROOT.gStyle.SetPalette(1)

# common/global items are defined here, mainly
# 
#  * file name
#  * year/era 
#  * output dir name 
# 
def setdefaults(is2017, filename):
    ## all defaults here
    f2018 = ROOT.TFile('rootfiles/PrefiringRateEE_2017data.root','READ')

    dirname=''
    if is2017: 
        dirname = 'Plots2017_FrontTrain/'
        #f2018   = ROOT.TFile('PrefiringRateEE_2017data.root','READ')
        f2018   = ROOT.TFile(filename,'READ')


    if not is2017:
        dirname = 'Plots2018_FrontTrain/'
        f2018   = ROOT.TFile(filename,'READ')

    os.system('mkdir '+dirname)


    toreturn = [f2018, dirname, is2017]
    return toreturn


def SetCMSAxis(h, xoffset=1., yoffset=1.):
    h.GetXaxis().SetTitleSize(0.047)
    h.GetYaxis().SetTitleSize(0.047)
    
    print (type(h))
    if type(h) is ( (not TGraphAsymmErrors) or (not TGraph)):  h.GetZaxis().SetTitleSize(0.047)
    
    h.GetXaxis().SetLabelSize(0.047)
    h.GetYaxis().SetLabelSize(0.047)
    if type(h) is ( (not TGraphAsymmErrors) or (not TGraph)): h.GetZaxis().SetLabelSize(0.047)
    
    

    h.GetXaxis().SetTitleOffset(xoffset)
    h.GetYaxis().SetTitleOffset(yoffset)

    
    
    return h


def ExtraText(text_,x_, y_):
    if not text_: print "nothing provided as text to ExtraText, function crashing"
    ltx = TLatex()
    
    if len(text_)>0:
        ltx.SetTextFont(42)
        ltx.SetTextSize(0.049)
        ltx.DrawTextNDC(x_,y_,text_)
    return ltx



# This function define  a canvas which is as per CMS Style, This still need changes to be in 100% sync with CMS Style
#   * This is for 2d plot
#   * Or a 1d plot which does not need a ratio plot. 
#   * for a ratio plot new canvas size is needed see another function for this purpose. 
#   * Following two are still under development. 
#   * myCanvasRatio(): if there is just one ratio plot needed 
#   * myCanvasRatio2(): if there are two ratio plots needed in the same canvas 

def myCanvas():
    c = ROOT.TCanvas("myCanvasName","The Canvas Title",800,600)
    c.SetBottomMargin(0.1)
    c.SetRightMargin(0.20)
    c.SetLeftMargin(0.1)
    return c


def myCanvas1D():
    c = ROOT.TCanvas("myCanvasName","The Canvas Title",650,600)
    c.SetBottomMargin(0.1)
    c.SetRightMargin(0.050)
    c.SetLeftMargin(0.15)
    return c


# This is a generalised function that take TH2F and save it into PDF, this require in order 
#    * 2d histogram
#    * canvas 
#    * x title name 
#    * Y title name 
#    * in future if needed offset can be configured too with default values set to 0.7 
#    * in future, Draw option for the 2D histogram can be added, COLZ by default. 
#    * last two options are not yet used in present version of the code. 

def Save2DHisto(h2,c, xname, yname,offset=0.75, drawtype="COLZ"):
    h2.Draw("")
    h2.SetMarkerSize(1.5)
    h2.GetXaxis().SetTitle(xname)
    h2.GetYaxis().SetTitle(yname)
    h2.GetXaxis().SetTitleOffset(1.)
    h2.GetYaxis().SetTitleOffset(1.25)
    
    return h2


# histogram to set the offset and linewidth etc for a 1d plot. 

def Save1DHisto(h1,c, xname, yname):
    h1.GetXaxis().SetTitle(xname)
    h1.GetYaxis().SetTitle(yname)
    h1.SetLineColor(1)
    h1.SetLineWidth(3)
    h1.GetXaxis().SetTitleOffset(1.)
    h1.GetYaxis().SetTitleOffset(1.25)
    h1.Draw()
    return h1

def SetLegend(coordinate_=[.15,.7,.47,.87],ncol=1):
    c_=coordinate_
    legend=TLegend(c_[0], c_[1],c_[2],c_[3])
    legend.SetBorderSize(0)
    legend.SetNColumns(ncol)
    legend.SetLineColor(1)
    legend.SetLineStyle(1)
    legend.SetLineWidth(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize(0.05)

    
    return legend

# This function takes the input as which year it is, Based on this information it draw the legend related to year, energy and lumi. 
#  * at present 2017 and 2018 legends are added, 
#  * For future, add 2019 legend. 
#  * For future, add lumi value, 

def drawenergy(is2017, data=True):
    pt = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)
    
    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize *0.7
    pt.SetTextSize(cmstextSize)
    text = pt.AddText(0.01,0.57,"#font[61]{CMS}")
    
    pt1 = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.155,0.4,"Preliminary")
    text1 = pt1.AddText(0.125,0.4,"Work in progress 2017")
    
    pt2 = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)
#    text3 = pt2.AddText(0.53,0.5,"#sqrt{s} = 13 TeV(2017)")
    

    pavetext = ''
    if is2017 and data: pavetext = "(13 TeV)"
    if (not is2017) and data: pavetext = "(13 TeV)"

    if is2017 and not data: pavetext = "(13 TeV)"
    if (not is2017) and not data: pavetext = "(13 TeV)"

    if data: text3 = pt2.AddText(0.735,0.5,pavetext)
    if not data: text3 = pt2.AddText(0.75,0.5,pavetext)
    
    return [pt,pt1,pt2]



def drawenergy1D(is2017, text_="Work in progress 2018", data=True):
    pt = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)
    
    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize *0.7
    pt.SetTextSize(cmstextSize)
    text = pt.AddText(0.063,0.57,"#font[61]{CMS}")
    
    pt1 = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    text1 = pt1.AddText(0.215,0.4,text_)
    
    pt2 = TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)
#    text3 = pt2.AddText(0.53,0.5,"#sqrt{s} = 13 TeV(2017)")
    

    #pavetext = ''
    #if is2017: pavetext = "#sqrt{s} = 13 TeV(2017)"
    #if not is2017: pavetext = "#sqrt{s} = 13 TeV(2018)"
    #text3 = pt2.AddText(0.61,0.5,pavetext)
    
    pavetext = ''
    if is2017 and data: pavetext = "(13 TeV)"
    if (not is2017) and data: pavetext = "(13 TeV)"

    if is2017 and not data: pavetext = "13 TeV"
    if (not is2017) and not data: pavetext = "13 TeV"

    if data: text3 = pt2.AddText(0.81,0.5,pavetext)
    if not data: text3 = pt2.AddText(0.85,0.5,pavetext)
    
    return [pt,pt1,pt2]
    return [pt,pt1,pt2]



# This function plot 2d histo on the canvas and need following information (in order): 
#  * file object
#  * year
#  * dirname where output will be saved 
#  * name of the 2d histogram 
#  * x axis name 
#  * y axis name 
#  
#  In future, The name of the function should be changed by plotOnCanvas()

def savePDF(f2018, year, dirname, histname, xname, yname, postfix="", setlog=False):
    print "saving", histname
    h2 = f2018.Get(histname)
    #h2.Sumw2()
    c=myCanvas()
    h2 = Save2DHisto(h2,c, xname, yname)
    h2.Draw('COLZTEXT45')
    h2.SetMarkerSize(1.9)
    c.Draw()
    
    pt = drawenergy(year)
    #pt.Draw()
    
    histname = histname+"_"+postfix
    c.SaveAs(dirname+'/'+histname+'.pdf')
    c.SaveAs(dirname+'/'+histname+'.png')
    
    if setlog:
        c.SetLogz(1)
        c.SaveAs(dirname+'/'+histname+'_logZ.pdf')
        c.SaveAs(dirname+'/'+histname+'_logZ.png')
    return c




def savePDF1D(f2018, year, dirname, histname, xname, yname):
    print "saving", histname
    h1 = f2018.Get(histname)
    c=myCanvas()
    h1 = Save1DHisto(h1,c, xname, yname)
    h1.Draw()
    c.Draw()
    
    pt = drawenergy(year)
    #pt.Draw()
    
    c.SaveAs(dirname+'/pdf/'+histname+'.pdf')
    c.SaveAs(dirname+'/png/'+histname+'.png')

    c.SetLogz(1)
    c.SaveAs(dirname+'/pdflog/'+histname+'_logZ.pdf')
    c.SaveAs(dirname+'/pnglog/'+histname+'_logZ.png')
    return c


# * This function is still under progress. Make sure you understand this before using this one, 
# * do all necessary checks and add all options you might need to add in the input arguments. 
# 

def OverLay1D(files, dirname, histname, xname, yname, legend,year):
    os.system('mkdir '+dirname+'/pdf')
    os.system('mkdir '+dirname+'/pdflog')
    os.system('mkdir '+dirname+'/png')
    os.system('mkdir '+dirname+'/pnglog')


    #h1=[]
    c=myCanvas()
    c.Draw()
    pt = drawenergy(year)
    #pt.Draw()
    
    i=0
    for ifile in files:
        h1=ifile.Get(histname)
        h1 = Save1DHisto(h1,c, xname, yname)
        if i==0: h1.Draw()
        if i>0: h1.Draw("same")
        i=i+1
    

    
    c.SaveAs(dirname+'/pdf/'+histname+'.pdf')
    c.SaveAs(dirname+'/png/'+histname+'.png')

    c.SetLogz(1)
    c.SaveAs(dirname+'/pdflog/'+histname+'_logZ.pdf')
    c.SaveAs(dirname+'/pnglog/'+histname+'_logZ.png')


    return c


# Following function saves 2D and TProfile over Y axis on the same plot. This need following information in order: 
#  * file object 
#  * year: to plot the energy legend
#  * output dir name 
#  * 2d histo name 
#  * x axis name 
#  * y axis name 
#  
#  This can be renamed as plotOnCanvasTProfile() 


def savePDFTProfile(f2018, year, dirname, histname, xname, yname):
    h2 = f2018.Get(histname)
    #h2.Sumw2()
    #print h2.Integral()
    c=myCanvas()
    h2 = Save2DHisto(h2,c, xname, yname)
    h2.Draw('COLZ')
    h2.SetMarkerSize(1.9)
    h1 = h2.ProfileX()
    h1.Draw("E1same")
    h1.SetMarkerStyle(20)
    h1.SetMarkerSize(1.5)
    c.Draw()
    
    pt = drawenergy(year)
    #pt.Draw()


    
    c.SaveAs(dirname+'/'+histname+'_profile.pdf')
    c.SaveAs(dirname+'/'+histname+'_profile.png')
    
    c.SetLogz(1)
    c.SaveAs(dirname+'/'+histname+'_profile_logZ.pdf')
    c.SaveAs(dirname+'/'+histname+'_profile_logZ.png')


    
    return c


# In some cases one need to normalize the 2d histogram such that for a given X axis bin Y axis is normalised. The only input needed is the: 
#  * 2-d histogram and in output a normalised 2d histo is returned. 
# 

# In[35]:


def NormalizeYAxis(h2,axis_N="Y"):
    h2_new = h2.Clone()
    h2_new.SetDirectory(0)
    TH2.AddDirectory(0)
    
    if axis_N == "Y":
        for ibx in range(1, h2.GetNbinsX()+1):
            verticalsum = 0.0 
            for iby in range(1, h2.GetNbinsY()+1):
                verticalsum = verticalsum + h2.GetBinContent(ibx, iby)
                #print 'old bin content = ',ibx, iby,  h2.GetBinContent(ibx, iby)
            
            # once the sum is calculated this has to be used to scaling each bin content in the X bin i.e. 
            # divide each bin content by verticalsum 
            # following is outside the for loop of iby, create another loop for the Y axis. 
            for iby_ in range (1, h2.GetNbinsY()+1):
                new_content = 0.0 
                old_content = h2.GetBinContent(ibx, iby_)
                # safety check to avoid divide by zero. 
                if verticalsum != 0: new_content = old_content / verticalsum
                h2_new.SetBinContent(ibx, iby_, new_content)

                
                
                ## error calculation  
                error_ = 0.0 
                if verticalsum !=0:
                    delta_a  = math.sqrt(verticalsum) / verticalsum 
                    delta_b = 0.0
                    
                    if old_content > 0.0: delta_b  = math.sqrt(old_content) / old_content
                    error_ =  new_content * (delta_a + delta_b)
                h2_new.SetBinError(ibx,iby_, error_)
                h2_new.SetDirectory(0)
                TH2.AddDirectory(0)
                

                
             
    if axis_N == "X":
        for iby in range(1, h2.GetNbinsY()+1):
            verticalsum = 0.0 
            for ibx in range(1, h2.GetNbinsX()+1):
                verticalsum = verticalsum + h2.GetBinContent(ibx, iby)
                #print 'old bin content = ',ibx, iby,  h2.GetBinContent(ibx, iby)

            ## same as above but now normalised over X
            for ibx_ in range (1, h2.GetNbinsX()+1):
                new_content = 0.0 
                old_content = h2.GetBinContent(ibx_, iby)
                # safety check to avoid divide by zero. 
                if verticalsum != 0: new_content = old_content / verticalsum
                h2_new.SetBinContent(ibx_, iby, new_content)

                ## error calculation  
                error_ = 0.0 
                if verticalsum !=0:
                    delta_a  = math.sqrt(verticalsum) / verticalsum 
                    delta_b = 0.0
                    
                    if old_content > 0.0: delta_b  = math.sqrt(old_content) / old_content
                    error_ =  new_content * (delta_a + delta_b)
                h2_new.SetBinError(ibx_,iby, error_)
                h2_new.SetDirectory(0)
                TH2.AddDirectory(0)
    
    return h2_new


# In[36]:

## ----------------------------------------------------------------------------------------------
##    Description 
##
## this function will take a 2D histogram and normalize the two columns as per following formula 
## probability  =                  total sum for BX(-1)  
##                  ---------------------------------------------------
##                    [total sum for BX(-1) + total sum for BX(0) ]
## 
## ----------------------------------------------------------------------------------------------

def NormalizedPrefiringProbability(h2,axis_N="Y", binN_=1):
    ## binN_ = 1 for prefiring 
    ## binN_ = 3 for postfiring 
    
    h2_new = h2.Clone()
    h2_new.SetDirectory(0)
    TH2.AddDirectory(0)
    
    Vsum_=[]
    if axis_N == "Y":
        for ibx in range(1, h2.GetNbinsX()+1):
            verticalsum = 0.0 
            for iby in range(1, h2.GetNbinsY()+1):
                verticalsum = verticalsum + h2.GetBinContent(ibx, iby)
                #print 'old bin content = ',ibx, iby,  h2.GetBinContent(ibx, iby)
            Vsum_.append(verticalsum)


    if axis_N == "X":
        for iby in range(1, h2.GetNbinsY()+1):
            verticalsum = 0.0 
            for ibx in range(1, h2.GetNbinsX()+1):
                verticalsum = verticalsum + h2.GetBinContent(ibx, iby)
                #print 'old bin content = ',ibx, iby,  h2.GetBinContent(ibx, iby)
            Vsum_.append(verticalsum)
    
    print "Vsum_ = ", Vsum_
    prob_ = 0.
    if (Vsum_[binN_]+Vsum_[2]) > 0.0:
        prob_ = Vsum_[binN_]/(Vsum_[binN_]+Vsum_[2]) 
    delta_a = 0.0
    if Vsum_[binN_]>0.0: delta_a = math.sqrt(Vsum_[binN_])/Vsum_[binN_]
    delta_b = 0.0 
    if (Vsum_[binN_]+Vsum_[2])>0: delta_b = math.sqrt(Vsum_[binN_]+Vsum_[2]) / (Vsum_[binN_]+Vsum_[2])
    
    prob_e_ = prob_ * (delta_a + delta_b)
    return [prob_,prob_e_]



# This function does the task of calling all other helper function and saving the plot/canvas as pdf/png in a given directory. It need following input in order: 
#  * file object
#  * year for legend
#  * name of the histogram
#  * x axis name 
#  * y axis name 
#  
#  In future, all these 5 information can be saved in a single object and passed to each function so that one doesn;t need to send them everytime too many parameters, in addition, a parser can be written which will give required values whenever needed anywhere in the code. 
#  


def saveNormalised2DWithTProfile(f2018, year, dirname, histname, xname, yname, postfix="", isprofile=False, axis_N="Y",setlog=False):
    print " axis_N in the saveNormalised2DWithTProfile ", axis_N
    h2 = f2018.Get(histname)
    h2.SetDirectory(0)
    h2.AddDirectory(0)
    c=myCanvas()
    h2 = Save2DHisto(h2,c, xname, yname)
    h2 = NormalizeYAxis(h2, axis_N)
    h2.GetXaxis().SetNdivisions(505)
    h2.GetYaxis().SetNdivisions(505)
    h2.Draw('COLZ TEXT  E')

    #h2.Draw('COLZTEXT')
    h2.SetMarkerSize(2.)
    h2.SetMarkerColor(1)
    
    h2=SetCMSAxis(h2)
    tt = ExtraText("ECAL",0.132, 0.8)
    tt.Draw()
    
    tt1 = ExtraText("Endcaps",0.113, 0.75)
    tt1.Draw()
    
    if isprofile:
        h1 = h2.ProfileX()
        h1.Draw("same")
        h1.SetMarkerStyle(20)
        h1.SetMarkerSize(1.5)
        histname  = histname + "_profile"
        
    c.Draw()
    
    pt = drawenergy(year)
    
    for ipt in pt: ipt.Draw()

    
    
    histname = histname + "_" + postfix + "_" + axis_N
        
    
    
    c.SaveAs(dirname+'/'+histname+'.pdf')
    c.SaveAs(dirname+'/'+histname+'.png')
    
    print "setlog -------", setlog
    if setlog: 
        c.SetLogz(1)
        c.SaveAs(dirname+'/'+histname+'_logZ.pdf')
        c.SaveAs(dirname+'/'+histname+'_logZ.png')


    
    return c




def TextToGraphTimeScan(textfilename):
    dirname="timescanOutput/"
    #filenames=['timescanOutput/Rate_2017data_FrontTrain_cutval_2.txt','timescanOutput/Rate_2017data_FrontTrain_cutval_4.txt','timescanOutput/Rate_2017data_FrontTrain_cutval_6.txt','timescanOutput/Rate_2017data_FrontTrain_cutval_8.txt','timescanOutput/Rate_2017data_FrontTrain_cutval_10.txt']
    filename = textfilename
    f = open(filename,"r").readlines()
    firstLine = f.pop(0) #removes the first line

    
    adc_        =  array('f')
    adc_1       =  array('f')
    adc_2       =  array('f')
    adc_3       =  array('f')
    adc_4       =  array('f')
    
    prob        =  array('f')
    prob_e      =  array('f')
    
    prob_26     =  array('f')
    prob_e_26   =  array('f')
    
    prob_27     =  array('f')
    prob_e_27   =  array('f')
    
    prob_28     =  array('f')
    prob_e_28   =  array('f')

    prob_29     =  array('f')
    prob_e_29   =  array('f')
    
    errx        =  array('f')
    

    for line in f:
        adc_.append(      float(  line.rstrip().split()[0]))
        adc_1.append(      float(  line.rstrip().split()[0]) + 0.1)
        adc_2.append(      float(  line.rstrip().split()[0]) + 0.2)
        adc_3.append(      float(  line.rstrip().split()[0]) + 0.3)
        adc_4.append(      float(  line.rstrip().split()[0]) + 0.4)

        prob.append(      float(  line.rstrip().split()[1]) )
        prob_e.append(    float(  line.rstrip().split()[2]) )
        
        prob_26.append(   float(  line.rstrip().split()[3]) )
        prob_e_26.append( float(  line.rstrip().split()[4]) )
        
        prob_27.append(   float(  line.rstrip().split()[5]) )
        prob_e_27.append( float(  line.rstrip().split()[6]) )
        
        prob_28.append(   float(  line.rstrip().split()[7]) )
        prob_e_28.append( float(  line.rstrip().split()[8]) )
        
        prob_29.append(   float(  line.rstrip().split()[9]) )
        prob_e_29.append( float(  line.rstrip().split()[10]) )
        
        errx.append(0.0)
        
    #adc_1 = [i+0.1 for i in adc_]
    #adc_2 = [i+0.2 for i in adc_]
    #adc_3 = [i+0.3 for i in adc_]
    #adc_4 = [i+0.4 for i in adc_]

    print adc_1
    
    g_prob_     = TGraphAsymmErrors(int(len(adc_)),   adc_,   prob,     errx, errx, prob_e,    prob_e    )   ;  g_prob_.SetName("prob_")
    g_prob_26_  = TGraphAsymmErrors(int(len(adc_1)),   adc_1,   prob_26,  errx, errx, prob_e_26, prob_e_26 )   ;  g_prob_26_.SetName("prob_26_")
    g_prob_27_  = TGraphAsymmErrors(int(len(adc_)),   adc_2,   prob_27,  errx, errx, prob_e_27, prob_e_27 )   ;  g_prob_27_.SetName("prob_27_")
    g_prob_28_  = TGraphAsymmErrors(int(len(adc_)),   adc_3,   prob_28,  errx, errx, prob_e_28, prob_e_28 )   ;  g_prob_28_.SetName("prob_28_")
    g_prob_29_  = TGraphAsymmErrors(int(len(adc_)),   adc_4,   prob_29,  errx, errx, prob_e_29, prob_e_29 )   ;  g_prob_29_.SetName("prob_29_")


        
    f1 = TFile(filename.replace('.txt','.root'), 'RECREATE')
    
    g_prob_.Write()
    g_prob_26_.Write()
    g_prob_27_.Write()
    g_prob_28_.Write()
    g_prob_29_.Write()
    
    f1.Close()








def PseudoTextToGraphTimeScan(textfilename):
    print "parsing: ", textfilename
    dirname="timescanOutput/"
    filename = textfilename
    f = open(filename,"r").readlines()
    firstLine = f.pop(0) #removes the first line

    
    adc_        =  array('f')
    adc_1       =  array('f')
    adc_2       =  array('f')
    adc_3       =  array('f')
    adc_4       =  array('f')
    
    prob        =  array('f')
    prob_e      =  array('f')
    
    errx        =  array('f')
    

    for line in f:
        adc_.append(      float(  line.rstrip().split()[0]))
        adc_1.append(      float(  line.rstrip().split()[0]) + 0.1)
        adc_2.append(      float(  line.rstrip().split()[0]) + 0.2)
        adc_3.append(      float(  line.rstrip().split()[0]) + 0.3)
        adc_4.append(      float(  line.rstrip().split()[0]) + 0.4)

        prob.append(      float(  line.rstrip().split()[1]) )
        prob_e.append(    float(  line.rstrip().split()[2]) )
        
        errx.append(0.0)
        
        
    g_prob_     = TGraphAsymmErrors(int(len(adc_)),   adc_,   prob,     errx, errx, prob_e,    prob_e    )   ;  g_prob_.SetName("prob_")


        
    f1 = TFile(filename.replace('.txt','.root'), 'RECREATE')
    
    g_prob_.Write()
    f1.Close()




