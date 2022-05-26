import sys
import PyFrensie.Geometry as Geometry
import PyFrensie.Geometry.DagMC as DagMC
import PyFrensie.Utility as Utility
import PyFrensie.Utility.MPI as MPI
import PyFrensie.Utility.Prng as Prng
import PyFrensie.Utility.Coordinate as Coordinate
import PyFrensie.Utility.Distribution as Distribution
import PyFrensie.MonteCarlo as MonteCarlo
import PyFrensie.MonteCarlo.Collision as Collision
import PyFrensie.MonteCarlo.ActiveRegion as ActiveRegion
import PyFrensie.MonteCarlo.Event as Event
import PyFrensie.MonteCarlo.Manager as Manager
import PyFrensie.Data as Data
import PyFrensie.Data.Native as Native

##---------------------------------------------------------------------------##
## Harcode the required parameters
##---------------------------------------------------------------------------##
# sim_name is of type string
sim_name = "sphere"

# db_path is of type string
db_path = "/home/simulator/data/mcnpdata/database.xml" 

# num_particles is of type float
num_particles = float(1)

# source_energy in MeV 
source_energy = float(1)

# energy_bins is a double array, in units of MeV
energy_bins = [0,0.5,1]

# thread is of type "int"
threads = int(4)

# history number to start at
history_N = int(10)

# not sure if we need
log_file = None 

##---------------------------------------------------------------------------##
## Initialize the MPI Session
##---------------------------------------------------------------------------##
session = MPI.GlobalMPISession( len(sys.argv), sys.argv )

# Suppress logging on all procs except for the master (proc=0)
Utility.removeAllLogs()
session.initializeLogs( 0, True )

if not log_file is None:
    session.initializeLogs( log_file, 0, True )

##---------------------------------------------------------------------------##
## Set the simulation properties
##---------------------------------------------------------------------------##
simulation_properties = MonteCarlo.SimulationProperties()

# Simulate neutrons only
simulation_properties.setParticleMode( MonteCarlo.NEUTRON_MODE )
simulation_properties.setUnresolvedResonanceProbabilityTableModeOff()

# Set the number of histories to run and the number of rendezvous
simulation_properties.setNumberOfHistories( num_particles )
# simulation_properties.setMinNumberOfRendezvous( 2 )
# simulation_properties.setMaxRendezvousBatchSize( 50 )

##---------------------------------------------------------------------------##
## Set up the materials
##---------------------------------------------------------------------------##
# Load the database
database = Data.ScatteringCenterPropertiesDatabase( db_path )

# Set the definition of H2O for this simulation and extract the properties for H2O from the database
scattering_center_definitions = Collision.ScatteringCenterDefinitionDatabase()

# Hydrogen 1 at RT
nuclide_properties = database.getNuclideProperties( Data.ZAID(1001) )
nuclide_definition = scattering_center_definitions.createDefinition( "H1", Data.ZAID(1001) )
nuclide_definition.setNuclearDataProperties( nuclide_properties.getSharedNuclearDataProperties( Data.NuclearDataProperties.ACE_FILE, 8, 293.6 , False ) )

# Oxygen 16 at RT
nuclide_properties = database.getNuclideProperties( Data.ZAID(8016) )
nuclide_definition = scattering_center_definitions.createDefinition( "O16", Data.ZAID(8016) )
nuclide_definition.setNuclearDataProperties( nuclide_properties.getSharedNuclearDataProperties( Data.NuclearDataProperties.ACE_FILE, 8, 293.6 , False ) )

material_definitions = Collision.MaterialDefinitionDatabase()
material_definitions.addDefinition( "light_water", 1 , ["H1","O16"], [-0.111894,-0.888106] )

##---------------------------------------------------------------------------##
## Set up the geometry
##---------------------------------------------------------------------------##
# Set the model properties before loading the model
model_properties = DagMC.DagMCModelProperties( "sphere.h5m" )
model_properties.setMaterialPropertyName( "mat" )
model_properties.setDensityPropertyName( "rho" )
model_properties.setTerminationCellPropertyName( "termination.cell" )
model_properties.setSurfaceFluxName( "surface.flux" )
model_properties.setSurfaceCurrentName( "surface.current" )
model_properties.useFastIdLookup()

# Load the model
model = DagMC.DagMCModel( model_properties )

# Fill the model with the defined materials
filled_model = Collision.FilledGeometryModel( db_path, scattering_center_definitions, material_definitions, simulation_properties, model, True )

##---------------------------------------------------------------------------##
## Set up the source
##---------------------------------------------------------------------------##
# Define the generic particle distribution
particle_distribution = ActiveRegion.StandardParticleDistribution( "source distribution" )

particle_distribution.setEnergy( source_energy )
particle_distribution.setPosition( 0.0, 0.0, 0.0 )
particle_distribution.constructDimensionDistributionDependencyTree()

# The generic distribution will be used to generate neutrons
neutron_distribution = ActiveRegion.StandardNeutronSourceComponent( 0, 1.0, model, particle_distribution )

# Assign the neutron source component to the source
source = ActiveRegion.StandardParticleSource( [neutron_distribution] )

##---------------------------------------------------------------------------##
## Set up the event handler
##---------------------------------------------------------------------------##
# The model must be passed to the event handler so that the estimators
# defined in the model can be constructed
event_handler = Event.EventHandler( model, simulation_properties )

# Set the energy and collision number bins as estimator 1
event_handler.getEstimator( 1 ).setEnergyDiscretization(energy_bins )

# Set the energy and collision number bins as estimator 2
event_handler.getEstimator( 2 ).setEnergyDiscretization( energy_bins )

##---------------------------------------------------------------------------##
## Set up the simulation manager
##---------------------------------------------------------------------------##
# The factory will use the simulation properties and the MPI session
# properties to determine the appropriate simulation manager to construct
# Use start at N constructor
factory = Manager.ParticleSimulationManagerFactory( filled_model,
                                                    source,
                                                    event_handler,
                                                    simulation_properties,
                                                    history_N,
                                                    sim_name,
                                                    "xml",
                                                    threads )


# Create the simulation manager
manager = factory.getManager()

# Initialize RNG to start at history N
# This does work, but the runInterruptibleSimulation() resets to zero and launches
# in batches at the correct histories so each processor handles a separate set of them

# Turn on multiple rendezvous files
manager.useMultipleRendezvousFiles()

# Allow logging on all procs
session.restoreOutputStreams()

##---------------------------------------------------------------------------##
## Run the simulation
##---------------------------------------------------------------------------##

if session.size() == 1:
    manager.runInterruptibleSimulation()
else:
    manager.runSimulation()

