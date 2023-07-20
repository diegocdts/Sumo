import os
from datetime import datetime

import sumolib


def run_id():
    return f'sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'


def dir_exists_create(dir_name: str):
    path = os.path.join(os.path.normpath(os.getcwd()), dir_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

class SimulationSettings:

    def __init__(self, args):
        self.scenario_path = args.scenario_path
        self.trace_path = dir_exists_create(f'{self.scenario_path}/{run_id()}')
        self.fm_path = dir_exists_create(f'{self.trace_path}_fm')

        self.simulation_time = args.simulation_time
        self.window_size = args.window_size
        self.resolution = args.cell_resolution

        self.sumoCmd = ['sumo', '-c', f'{self.scenario_path}/osm.sumocfg']
        self.net = sumolib.net.readNet(f'{self.scenario_path}/osm.net.xml.gz')

        boundary = self.net.getBoundary()

        min_x, min_y = boundary[0], boundary[1]
        max_x, max_y = boundary[2], boundary[3]

        self.width = int((max_x - min_x) / self.resolution)
        self.height = int((max_y - min_y) / self.resolution)

