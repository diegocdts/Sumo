import warnings

from components.settings import SimulationSettings
from components.simulation import Simulation, arguments
from components.instances import parameters, properties

warnings.filterwarnings("ignore")

args = arguments()

settings = SimulationSettings(args)

properties.set_input_shape(settings.width, settings.height)

Simulation(settings, parameters, properties)
