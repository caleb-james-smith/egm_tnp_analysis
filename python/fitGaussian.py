# fitGaussian.py

import os
import ROOT
from ROOT import RooRealVar, RooDataHist, RooGaussian, RooPlot

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

def fit_gaussian():
    plot_dir = "plots"
    makeDir(plot_dir)
    
    # Create a histogram and fill it with random Gaussian data
    hist = ROOT.TH1F("hist", "Gaussian Histogram;X;Entries", 100, -10, 10)
    rnd = ROOT.TRandom()
    for i in range(10000):
        hist.Fill(rnd.Gaus(0, 2))  # Gaussian distribution with mean 0 and sigma 2

    # Define the observable variable for RooFit
    x = RooRealVar("x", "x", -10, 10)

    # Import the histogram into a RooDataHist
    data = RooDataHist("data", "dataset with x", ROOT.RooArgList(x), hist)

    # Define the parameters for the Gaussian model
    mean = RooRealVar("mean", "mean", 0, -10, 10)
    sigma = RooRealVar("sigma", "sigma", 2, 0.1, 10)
    
    # Define the Gaussian model
    gauss = RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

    # Fit the Gaussian model to the data
    gauss.fitTo(data)

    # Create a canvas to display the results
    c = ROOT.TCanvas("c", "Gaussian Fit", 800, 600)
    
    # Create a RooPlot to visualize the fit results
    xframe = x.frame(ROOT.RooFit.Title("Gaussian Fit"))
    
    # Plot the data and the fit result on the RooPlot
    data.plotOn(xframe)
    gauss.plotOn(xframe)

    # Draw the RooPlot on the canvas
    xframe.Draw()

    # Save the canvas as an image file
    plot_name = "{0}/gaussian_fit.pdf".format(plot_dir)
    c.SaveAs(plot_name)

if __name__ == "__main__":
    fit_gaussian()

