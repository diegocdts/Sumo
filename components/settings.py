import argparse
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

        - sumoCmd: access to the osm.sumocfg simulation file

        - net: access to the osm.net.xml.gz simulation file

        :param args: parsed arguments
        """
        self.scenario_path = args.scenario_path
        self.trace_path = dir_exists_create(f'{self.scenario_path}/{run_id()}')

        self.sumoCmd = ['sumo', '-c', f'{self.scenario_path}/osm.sumocfg']
        self.net = sumolib.net.readNet(f'{self.scenario_path}/osm.net.xml.gz')


def arguments():
    """
    sets the required arguments to run SUMO simulations
    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Required arguments to run SUMO simulations')
    parser.add_argument('--scenario_path', type=str, default='None', help='The relative path of the scenario')

    return parser.parse_args()
