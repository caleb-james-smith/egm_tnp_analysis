# massHistFitGauss.py

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

# Analyze root file
def analyze(file_name, variable, cuts = ""):
    print("file name: {0}".format(file_name))
    
    plot_dir = "plots"
    makeDir(plot_dir)
    
    # Load canvas from root file
    canvas_name = "Canvas_1"
    f = ROOT.TFile(file_name)
    c = f.Get(canvas_name)

    # Check for errors when loading canvas
    if not c:
        print("ERROR: Unable to load this canvas: {0}".format(canvas_name))
        f.Close()
        return

    # Get list of primitives from canvas
    primitives = list(c.GetListOfPrimitives())

    # Print primitives
    print("Primitives:")
    for p in primitives:
        print(" - {0}: {1}".format(type(p), p))

    # Load histogram
    hist_name = "htemp"
    h = c.GetPrimitive(hist_name)
    print("h: {0}".format(h))

    # Declare observable x
    x = ROOT.RooRealVar("x", "invariant mass [GeV]", 50, 130)

    # Import the histogram into a RooDataHist
    data = ROOT.RooDataHist("data", "dataset with x", ROOT.RooArgList(x), h)

    # Define the parameters for the Gaussian model
    mean    = ROOT.RooRealVar("mean", "mean", 91, 50, 130)
    sigma   = ROOT.RooRealVar("sigma", "width", 10, 0.1, 50)
    
    # Define the Gaussian model
    gauss   = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)

    # Fit the Gaussian model to the data
    gauss.fitTo(data)
    
    # Create a canvas to display the results
    new_c = ROOT.TCanvas("c", "Gaussian Fit", 800, 600)
    new_c.cd()
    
    # Create a RooPlot to visualize the fit results
    xframe = x.frame(ROOT.RooFit.Title("Gaussian Fit to Invariant Mass"))
    
    # Plot the data and the fit result on the RooPlot
    data.plotOn(xframe)
    gauss.plotOn(xframe)
    
    # Draw the RooPlot on the canvas
    xframe.Draw()
    
    # Define plot name
    if cuts:
        plot_name = "{0}/{1}_{2}_gauss_fit.pdf".format(plot_dir, variable, cuts)
    else:
        plot_name = "{0}/{1}_gauss_fit.pdf".format(plot_dir, variable)
    
    # Save the canvas as an image file
    new_c.Update()
    new_c.SaveAs(plot_name)

    # Delete objects
    del f
    del c
    del new_c

def main():
    file_name = "massHist.root"
    analyze(file_name, "mass")
    
if __name__ == "__main__":
    main()

