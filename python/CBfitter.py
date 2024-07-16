import os
import ROOT
from ROOT import TCanvas, TFile, gBenchmark, gStyle, gROOT, RooRealVar, RooDataHist, RooArgList, RooGaussian, RooPolynomial, RooAddPdf, RooFit, RooFitResult
ROOT.gROOT.LoadMacro('./libCpp/RooDoubleCBFast.cc+')

# Make sure ROOT.TFile.Open(fileURL) does not seg fault when $ is in sys.argv (e.g. $ passed in as argument)
ROOT.PyConfig.IgnoreCommandLineOptions = True
# Make plots faster without displaying them
ROOT.gROOT.SetBatch(ROOT.kTRUE)
# Tell ROOT not to be in charge of memory, fix issue of histograms being deleted when ROOT file is closed:
ROOT.TH1.AddDirectory(False)
 
# Create directory if it does not exist
def makeDir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def analyze(file_name, variable, cuts=""):
    print("file name: {0}".format(file_name))

    plot_dir = "plots"
    makeDir(plot_dir)

    canvas_name = "Canvas_1"
    f = ROOT.TFile(file_name)
    c = f.Get(canvas_name)

    if not c:
        print("ERROR: Unable to load this canvas: {0}".format(canvas_name))
        f.Close()
        return

    primitives = list(c.GetListOfPrimitives())

    print("Primitives:")
    for p in primitives:
        print(" - {0}: {1}".format(type(p), p))

    hist_name = "htemp"
    h = c.GetPrimitive(hist_name)

    x = ROOT.RooRealVar("x", "invariant mass [GeV]", 2.00, 4.0)
    data = ROOT.RooDataHist("data", "dataset with x", ROOT.RooArgList(x), h)
    
    # Define parameters for first crystalball shape
    mean1 = ROOT.RooRealVar("mean1", "mean1", 3.001, 2.9, 3.1)
    sigma1 = ROOT.RooRealVar("sigma1", "width1", 0.1, 0.1, 0.5)
    alpha1 = ROOT.RooRealVar("alpha1", "alpha1", 2.0, 0.1, 5.0)
    n1 = ROOT.RooRealVar("n1", "n1", 1, 0, 10)
    cb1 = ROOT.RooCBShape("cb1", "Crystal Ball 1", x, mean1, sigma1, alpha1, n1)

    # Define parameters for second crystalball shape
    mean2 = ROOT.RooRealVar("mean2", "mean2", 3.001, 2.9, 3.1)
    sigma2 = ROOT.RooRealVar("sigma2", "width2", 0.233, 0.01, 1)
    alpha2 = ROOT.RooRealVar("alpha2", "alpha2", 2, 0.1, 5)
    n2 = ROOT.RooRealVar("n2", "n2", 1, 0, 10)
    cb2 = ROOT.RooCBShape("cb2", "Crystal Ball 2", x, mean2, sigma2, alpha2, n2)


    cb3 = ROOT.RooDoubleCBFast("cb3", "double crystal ball", x, mean1, sigma1, alpha1, n1, alpha2, n2)
    #cb1 = ROOT.RooCBShape("cb1", "Crystal Ball 1", x, mean1, sigma1, sigma2, alpha1, n1, alpha2, n2)
    cb4 = ROOT.RooDoubleCBFast("cb4", "double crystal ball", x, mean2, sigma2, alpha1, n1, alpha2, n2) 
    # Define parameters for linear fit shape
    a0 = ROOT.RooRealVar("a0", "a0", 0, -1, 2)
    a1 = ROOT.RooRealVar("a1", "a1", 0, -1, 2)
    linear_bkg = ROOT.RooPolynomial("linear_bkg", "Linear Background", x, ROOT.RooArgList(a1))

    #exp_param = ROOT.RooRealVar("exp_param", "exponential parameter", -0.5, -5, 0)
    #exp_bkg = ROOT.RooExponential("exp_bkg", "Exponential Background", x, exp_param)




    nsig1 = ROOT.RooRealVar("nsig1", "number of signal events 1", 45000, 0, 98000)
    nsig2 = ROOT.RooRealVar("nsig2", "number of signal events 2", 45000, 0, 98000)
    nbkg = ROOT.RooRealVar("nbkg", "number of background events", 45000, 0, 98000)

    model = ROOT.RooAddPdf("model", "Double Crystal Ball + Linear Background", ROOT.RooArgList(cb3, cb4, linear_bkg),ROOT.RooArgList(nsig1, nsig2, nbkg))
    #model = ROOT.RooAddPdf("model", "Double Crystal Ball + Linear Background", ROOT.RooArgList(cb3, cb4, linear_bkg),ROOT.RooArgList(nsig1, nsig2, nbkg))

    #model = ROOT.RooAddPdf("model", "Double Crystal Ball + Linear Background", ROOT.RooArgList(cb1, cb2, exp_bkg),ROOT.RooArgList(nsig1, nsig2, nbkg))                

    model.fitTo(data, ROOT.RooFit.Range("signal"))

    new_c = ROOT.TCanvas("c", "Crystal Ball Fit with Linear Background", 800, 600)
    new_c.cd()

    xframe = x.frame(ROOT.RooFit.Title("Crystal Ball Fit with Linear Background to Invariant Mass"))

    data.plotOn(xframe)
    model.plotOn(xframe)
    #model.plotOn(xframe, ROOT.RooFit.Components("exp_bkg"), ROOT.RooFit.LineColor(ROOT.kBlack),ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.Range(55, 125))

    model.plotOn(xframe, ROOT.RooFit.Components("linear_bkg"), ROOT.RooFit.LineColor(ROOT.kBlack),ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.Range(2.1, 3.95))
    #model.plotOn(xframe, ROOT.RooFit.Components("cb1"), ROOT.RooFit.LineColor(ROOT.kPink),ROOT.RooFit.LineStyle(ROOT.kDotted), ROOT.RooFit.Range(2.2, 3.9))
    #model.plotOn(xframe, ROOT.RooFit.Components("cb2"), ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kSolid), ROOT.RooFit.Range(2.5, 3.3))
    model.plotOn(xframe, ROOT.RooFit.Components("cb3"), ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kSolid), ROOT.RooFit.Range(2.1, 3.95))
    model.plotOn(xframe, ROOT.RooFit.Components("cb4"), ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.LineStyle(ROOT.kSolid), ROOT.RooFit.Range(2.1, 3.95))
    gStyle.SetOptStat("emr")
    h.Draw()

    xframe.Draw("same")

    xframe_cb = x.frame(ROOT.RooFit.Title("Crystal Ball Fit"))
    data.plotOn(xframe_cb)
    model.plotOn(xframe_cb, ROOT.RooFit.Components("cb3,cb4"), ROOT.RooFit.LineStyle(ROOT.kSolid))

    #model.plotOn(xframe_cb, ROOT.RooFit.Components("cb3,cb4,linear_bkg"), ROOT.RooFit.LineStyle(ROOT.kSolid))
    #model.plotOn(xframe_cb, ROOT.RooFit.Components("cb3,cb4"), ROOT.RooFit.LineStyle(ROOT.kSolid))
    chi2_cb = xframe_cb.chiSquare()

 
    stats_box = ROOT.TPaveText(0.7, 0.6, 1.0, 0.4, "NDC")
    stats_box.SetFillColor(0)
    stats_box.AddText(f"Mean: {mean1.getValV():.2f} +/- {mean1.getError():.2f}")
    stats_box.AddText(f"Sigma: {sigma1.getValV():.2f} +/- {sigma1.getError():.2f}")
    stats_box.AddText(f"nsig: {nsig1.getValV():.0f} +/- {nsig1.getError():.0f}")
    stats_box.AddText(f"n: {n1.getValV():.0f} +/- {n1.getError():.0f}")
    #stats_box.AddText(f"nbkg: {nbkg.getValV():.0f} +/- {nbkg.getError():.0f}")
    stats_box.AddText(f"Mean2: {mean2.getValV():.2f} +/- {mean2.getError():.2f}")
    stats_box.AddText(f"Sigma2: {sigma2.getValV():.2f} +/- {sigma2.getError():.2f}")
    stats_box.AddText(f"nsig2: {nsig2.getValV():.0f} +/- {nsig2.getError():.0f}")
    stats_box.AddText(f"n2: {n2.getValV():.0f} +/- {n2.getError():.0f}")
    stats_box.AddText(f"nbkg: {nbkg.getValV():.0f} +/- {nbkg.getError():.0f}")


    #chi2 = xframe.chiSquare()
    #stats_box.AddText(f"Chi2/NDF: {chi2:.2f}")
    stats_box.AddText(f"Chi2/NDF (CB): {chi2_cb:.2f}")
    stats_box.Draw()





    if cuts:
        plot_name = "{0}/{1}_{2}.pdf".format(plot_dir, variable, cuts)
    else:
        plot_name = "{0}/{1}.pdf".format(plot_dir, variable)

    new_c.Update()
    new_c.SaveAs(plot_name)

    del f
    del c
    del new_c

def main():
    #file_name = "/uscms_data/d3/bchild/ScientificLinux7/CMSSW_11_2_0/src/TnpData/BParking_2018/Canvas_1.root"
    file_name = "/uscms_data/d3/bchild/ScientificLinux7/CMSSW_11_2_0/src/tnpData/Run2_2018_BParking/Canvas_1.root"
    analyze(file_name, "tnpFit")

if __name__ == "__main__":
    main()

