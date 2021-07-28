import ROOT, sys
ROOT.gROOT.SetBatch(True)
sys.argv.append( '-b-' )

from ROOT import TFile, TH1F, TGraph, TGraphAsymmErrors, THStack, TCanvas, TLegend, TPad, gStyle, gPad



yields={'cat_2b_SR': {'dyjets': 0.0, 'wjets': 22.20210403483361, 'diboson': 2.7126081973547116, 'qcd': 1.220972150753127, 'zjets': 58.191099144518375, 'tt': 36.45679804321844, 'smh': 2.219508267240599, 'data': 130.7924231439829, 'prefit': 130.4273572936654, 'singlet': 11.56250780960545}, 'cat_2b_ZEE': {'dyjets': 8.565842381678522, 'wjets': 0.0, 'diboson': 0.19590814141553992, 'qcd': 0, 'zjets': 0.0, 'tt': 2.6435412508435547, 'smh': 0.2643498032120988, 'data': 14.332667101174593, 'prefit': 12.104349702596664, 'singlet': 0.691145209944807}, 'cat_2b_WMU': {'dyjets': 0.8931985243689269, 'wjets': 31.84433215856552, 'diboson': 1.169823509408161, 'qcd': 3.984559706877917, 'zjets': 0.0, 'tt': 47.65273295342922, 'smh': 1.1343303518369794, 'data': 108.8426638841629, 'prefit': 94.00012050569057, 'singlet': 21.03346949070692}, 'cat_2b_ZMUMU': {'dyjets': 11.862486328929663, 'wjets': 0.0, 'diboson': 0.38736344047356397, 'qcd': 0, 'zjets': 0.0, 'tt': 4.073441784246825, 'smh': 0.37202785955742, 'data': 17.967999214306474, 'prefit': 16.702830493450165, 'singlet': 0.9621141223469749}, 'cat_2b_TOPMU': {'dyjets': 1.4721618336625397, 'wjets': 14.581144168972969, 'diboson': 0.6670696322107688, 'qcd': 4.550582422409207, 'zjets': 0.0, 'tt': 228.84752858430147, 'smh': 0.5227184006944299, 'data': 286.04800140857697, 'prefit': 247.44266551733017, 'singlet': 33.12913604080677}, 'cat_2b_WE': {'dyjets': 0.4291441890527494, 'wjets': 22.56454000622034, 'diboson': 0.7104715318128001, 'qcd': 1.006525295110805e-06, 'zjets': 0.0, 'tt': 35.04791920259595, 'smh': 0.847300838213414, 'data': 76.73933346569538, 'prefit': 70.23511327803135, 'singlet': 16.06235135346651}, 'cat_2b_TOPE': {'dyjets': 1.0930875884369016, 'wjets': 10.707706451416016, 'diboson': 0.5591076138429116, 'qcd': 3.001812403090298, 'zjets': 0.0, 'tt': 181.71922187134624, 'smh': 0.4253868185915053, 'data': 222.8106667995453, 'prefit': 205.34005877375603, 'singlet': 26.409344375133514}}

processes = ["diboson", "qcd", "smh", "wjets", "singlet", "tt", "zjets", "dyjets", "data"]

regionlist = ["SR", "TOPE", "TOPMU", "WE", "WMU", "ZEE", "ZMUMU"]
regionlist_2b=["cat_2b_"+ir for ir in regionlist]

bins = regionlist_2b

nbins = len(bins)

postfix = "_2b"


def getprocess(yields, proc_name):
    h_crs = TH1F(proc_name+postfix, proc_name+postfix, nbins, 0,nbins)
    for ibin in range(len(bins)):
        yld_ = yields[bins[ibin]][proc_name]
        print "yld_: ", yld_
        h_crs.SetBinContent(ibin+1, yld_)
        h_crs.GetXaxis().SetBinLabel(ibin+1,bins[ibin])
        print "integral: ",h_crs.Integral()
    return h_crs


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

    
pad = myPad()
pad[1].cd()
gPad.SetLogy()

hs = THStack("hs", "")
for iproc in processes:
    if (iproc != "data") or  (iproc != "prefit"):
        hs.Add(getprocess(yields, iproc), "")
hs.Draw("hist")


pad[2].cd()
gPad.GetUymax()
hs.Draw("hist")


pad[0].Modified()
pad[0].Update()
pad[0].SaveAs("temp.pdf")
#pad[0].SaveAs(dirName_+region_+postfix+".png")
