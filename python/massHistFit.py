import ROOT
import os

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
    makeDir("plots")
    print("file name: {0}".format(file_name))
    
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

    # Set up model for Z mass fit
    x       = ROOT.RooRealVar("x", "x", 50, 130)
    mean    = ROOT.RooRealVar("mean", "mean of gaussian", 91, 50, 130)
    sigma   = ROOT.RooRealVar("sigma", "width of gaussian", 91, 0.1, 50)
    gauss   = ROOT.RooGaussian("gauss", "gaussian PDF", x, mean, sigma)
    
    # Draw histogram
    new_c = ROOT.TCanvas("c", "c", 800, 800)
    xframe = x.frame() 
    h.Draw()
    gauss.plotOn(xframe)

    # Save plot
    if cuts:
        plot_name = "plots/{0}_{1}.pdf".format(variable, cuts)
    else:
        plot_name = "plots/{0}.pdf".format(variable)
    
    new_c.Update()
    new_c.SaveAs(plot_name)

def main():
    file_name = "massHist.root"
    analyze(file_name, "mass")
    
if __name__ == "__main__":
    main()

