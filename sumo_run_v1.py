import warnings

from components.settings import SimulationSettings
from components.simulation import Simulation, arguments

warnings.filterwarnings("ignore")

args = arguments()

settings = SimulationSettings(args)
Simulation(settings)
