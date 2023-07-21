import os
from datetime import datetime

import sumolib


def run_id():
    """
    defines a simulation identifier for naming the trace output directory
    :return: the simulation identifier
    """
    return f'sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'


def dir_exists_create(dir_name: str):
    """
    checks if a path exists. If not, then creates the path and returns it
    :param dir_name: path to be checked
    :return: path created
    """
    path = os.path.join(os.path.normpath(os.getcwd()), dir_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


class SimulationSettings:

    def __init__(self, args):
        """
        Instantiates an object that contains all relevant information for the mobility simulation, such as:

        - scenario_path: the path for the files that describe a scenario

        - trace_path: the path for the trace output directory

        - dm_path: the path for the feature matrices directory

        - simulation_time: the duration of the simulation

        - temporal_resolution: the time interval for a sample (temporal resolution)

        - spatial_resolution: the cell resolution (spatial resolution)

        - window_size: the number of intervals inside a window

        - sumoCmd: access to the osm.sumocfg simulation file

        - net: access to the osm.net.xml.gz simulation file

        - width: cells width

        - height: cells height
        :param args: parsed arguments
        """
        self.scenario_path = args.scenario_path
        self.trace_path = dir_exists_create(f'{self.scenario_path}/{run_id()}')
        self.dm_path = dir_exists_create(f'{self.trace_path}_dm')

        self.simulation_time = args.simulation_time
        self.temporal_resolution = args.temporal_resolution
        self.spatial_resolution = args.spatial_resolution
        self.window_size = args.window_size

        self.sumoCmd = ['sumo', '-c', f'{self.scenario_path}/osm.sumocfg']
        self.net = sumolib.net.readNet(f'{self.scenario_path}/osm.net.xml.gz')

        boundary = self.net.getBoundary()

        min_x, min_y = boundary[0], boundary[1]
        max_x, max_y = boundary[2], boundary[3]

        self.width = int((max_x - min_x) / self.spatial_resolution)
        self.height = int((max_y - min_y) / self.spatial_resolution)
