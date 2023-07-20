from components.settings import SimulationSettings
from components.simulation import Simulation, arguments

args = arguments()

settings = SimulationSettings(args)
Simulation(settings)
