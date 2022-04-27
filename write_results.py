import os
import sys
import PyFrensie.Geometry.DagMC as DagMC
import PyFrensie.Utility as Utility
import PyFrensie.MonteCarlo as MonteCarlo
import PyFrensie.MonteCarlo.Event as Event
import PyFrensie.MonteCarlo.Manager as Manager
from optparse import *




# Parse the command line arguments
parser = OptionParser()
parser.add_option("--rendezvous_file", type="string", dest="rendezvous_file",
                    help="the rendezvous file to load")
parser.add_option("--NPS",type="string",dest="NPS",
                    help="the number of particles corresponding to the results")
options,args = parser.parse_args()


# Activate just-in-time initialization to prevent automatic loading of the
# geometry and data tables
Utility.activateJustInTimeInitialization()
# Reload the simulation
manager = Manager.ParticleSimulationManagerFactory( options.rendezvous_file ).getManager()
# Get estimators and energy bins for current
current = manager.getEventHandler().getEstimator( 1 ) # current is estimator 1 as declared in trelis script
current_bin_data = current.getEntityBinProcessedData( 1 ) # entity ID is 1 since sphere surface is first volume
current_bin_data["e_bins"] = current.getEnergyDiscretization()

# Get estimators and energy bins for flux
flux = manager.getEventHandler().getEstimator ( 2 ) # flux is estimator 2 as declared in trelis script
flux_bin_data = flux.getEntityBinProcessedData( 1 ) # entity ID is 1 since sphere surface is first volume
flux_bin_data["e_bins"] = flux.getEnergyDiscretization()



file_name = "sphere_results_"
file = open(file_name + options.NPS  + ".csv","w+")
file.write("current results" + "\n" )
file.write("energy bin upper bound" +  ", " + "current mean" + ", " + "current RE " + "\n" )
for i in range(0,len(current_bin_data["mean"])):
    file.write(str(current_bin_data["e_bins"][i+1]) +  ", " + str(current_bin_data["mean"][i]) + ", " + str(current_bin_data["re"][i]) + "\n" )
file.write("flux results" + "\n" )
for i in range(0,len(flux_bin_data["mean"])):
    file.write(str(flux_bin_data["e_bins"][i+1]) +  ", " + str(flux_bin_data["mean"][i]) + ", " + str(flux_bin_data["re"][i]) + "\n" )