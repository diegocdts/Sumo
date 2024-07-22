import warnings

from components.settings import SimulationSettings, arguments
from components.simulation import Simulation

warnings.filterwarnings("ignore")

args = arguments()  # parse arguments

settings = SimulationSettings(args)     # instantiate simulation settings

Simulation(settings)    # instantiates and runs one simulation
