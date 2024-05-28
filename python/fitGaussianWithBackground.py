# fitGaussianWithBackground.py

import os
import ROOT

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

# Fit gaussian with background
def fit_gaussian_with_background():
    plot_dir = "plots"
    makeDir(plot_dir)
    
    # Create a histogram and fill it with random Gaussian data + linear background
    hist = ROOT.TH1F("hist", "Gaussian Signal with Linear Background;X;Entries", 100, -10, 10)
    rnd = ROOT.TRandom()
    
    # Fill histogram with Gaussian signal
    for i in range(5000):
        hist.Fill(rnd.Gaus(0, 2))  # Gaussian distribution with mean 0 and sigma 2
    
    # Fill histogram with linear background
    for i in range(5000):
        hist.Fill(rnd.Uniform(-10, 10))  # Uniform distribution to simulate linear background

    # Define the observable variable for RooFit
    x = ROOT.RooRealVar("x", "x", -10, 10)

    # Import the histogram into a RooDataHist
    data = ROOT.RooDataHist("data", "dataset with x", ROOT.RooArgList(x), hist)

    # Define the parameters for the Gaussian signal
    mean  = ROOT.RooRealVar("mean", "mean", 0, -10, 10)
    sigma = ROOT.RooRealVar("sigma", "sigma", 2, 0.1, 10)
    gauss = ROOT.RooGaussian("gauss", "Gaussian Signal", x, mean, sigma)

    # Define the parameters for the linear background
    a0 = ROOT.RooRealVar("a0", "a0", 0, -1, 1)
    a1 = ROOT.RooRealVar("a1", "a1", 0, -1, 1)
    linear_bkg = ROOT.RooPolynomial("linear_bkg", "Linear Background", x, ROOT.RooArgList(a1))

    # Define the yields for signal and background
    nsig = ROOT.RooRealVar("nsig", "number of signal events", 5000, 0, 10000)
    nbkg = ROOT.RooRealVar("nbkg", "number of background events", 5000, 0, 10000)

    # Construct the total model as a sum of the Gaussian signal and the linear background
    model = ROOT.RooAddPdf("model", "Gaussian Signal + Linear Background", ROOT.RooArgList(gauss, linear_bkg), ROOT.RooArgList(nsig, nbkg))

    # Fit the model to the data
    model.fitTo(data)

    # Create a canvas to display the results
    c = ROOT.TCanvas("c", "Gaussian Fit with Linear Background", 800, 600)

    # Create a RooPlot to visualize the fit results
    xframe = x.frame(ROOT.RooFit.Title("Gaussian Fit with Linear Background"))
    
    # Plot the data and the fit result on the RooPlot
    data.plotOn(xframe)
    model.plotOn(xframe)
    model.plotOn(xframe, ROOT.RooFit.Components("linear_bkg"), ROOT.RooFit.LineStyle(ROOT.kDashed))
    model.plotOn(xframe, ROOT.RooFit.Components("gauss"), ROOT.RooFit.LineStyle(ROOT.kDotted))

    # Draw the RooPlot on the canvas
    xframe.Draw()

    # Save the canvas as an image file
    plot_name = "{0}/gaussian_fit_with_background.pdf".format(plot_dir)
    c.SaveAs(plot_name)

if __name__ == "__main__":
    fit_gaussian_with_background()

