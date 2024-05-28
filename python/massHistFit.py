import ROOT
import os

# Make sure ROOT.TFile.Open(fileURL) does not seg fault when $ is in sys.argv (e.g. $ passed in as argument)
ROOT.PyConfig.IgnoreCommandLineOptions = True
# Make plots faster without displaying them
ROOT.gROOT.SetBatch(ROOT.kTRUE)
# Tell ROOT not to be in charge of memory, fix issue of histograms being deleted when ROOT file is closed:
ROOT.TH1.AddDirectory(False)

# create directory if it does not exist
def makeDir(dir_name):
    if not os.path.exists(dir_name):
       os.makedirs(dir_name)

# analyze root file
def analyze(filename, variable, cuts = ""):
    makeDir("plots")
    print("file name: {0}".format(filename))
    
    # Load canvas from root file
    canvasname = "Canvas_1"
    f = ROOT.TFile(filename)
    c = f.Get(canvasname)
    #c.Draw()        

    # Check for errors when loading canvas
    if not c:
        print("ERROR: Unable to load this canvas: {0}".format(canvasname))
        f.Close()
        return

    # Get list of primitives from canvas
    primitives = list(c.GetListOfPrimitives())

    # Print primitives
    print("Primitives:")
    for p in primitives:
        print(" - {0}: {1}".format(type(p), p))

    # Load histogram
    h = c.GetPrimitive("htemp")
    print("h: {0}".format(h))
    
    # Draw histogram
    new_c = ROOT.TCanvas("c", "c", 800, 800)
    h.Draw()

    # Save plot
    if cuts:
        plotname = "plots/{0}_{1}.pdf".format(variable, cuts)
    else:
        plotname = "plots/{0}.pdf".format(variable)
    
    new_c.Update()
    new_c.SaveAs(plotname)

def main():
    filename = "massHist.root"
    analyze(filename, "mass")
    
if __name__ == "__main__":
    main()

