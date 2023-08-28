import warnings

from components.settings import SimulationSettings, arguments
from components.simulation import Simulation
from components.instances import parameters, properties

warnings.filterwarnings("ignore")

args = arguments()  # parse arguments

settings = SimulationSettings(args, properties)     # instantiate simulation settings

properties.set_input_shape(settings.width, settings.height)     # set the model input shape from scenario

Simulation(settings, parameters, properties)    # instantiates and runs one simulation
