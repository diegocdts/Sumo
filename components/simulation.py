import sys
import os
import csv
import time
import argparse
import traci

from datetime import datetime


class Simulation:
    def __init__(self, scenario_path):
        """
        Instantiates and starts a simulation, exporting raw mobility data of each moving object to its respective file.
        It creates one directory for each simulation round, identified by yyyy-mm-dd-H-M-S
        """
        self.scenario_path = abs_path(scenario_path)
        self.sim_mobility_output = f'{self.scenario_path}/sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'
        if not os.path.exists(self.sim_mobility_output):
            os.makedirs(self.sim_mobility_output)

        self.sumoCmd = ['sumo', '-c', f'{self.scenario_path}/osm.sumocfg']
        self.initial_time = self.get_epoch_time()
        self.run()

    @staticmethod
    def get_epoch_time():
        """
        :return: the current epoch time
        """
        epoch_time = int(time.time())
        return epoch_time

    def run(self):
        """
        runs a simulation
        """
        traci.start(self.sumoCmd)
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()

            self.write_trace(vehicles)

        traci.close()
        time.sleep(5)

    def write_trace(self, vehicles):
        """
        writes the current position of a moving object in its respective simulation file
        :param vehicles: the vehicles moving
        """
        for i in range(0, len(vehicles)):
            vehid = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicles[i])
            lon, lat = traci.simulation.convertGeo(x, y)

            record = [lat, lon, self.get_epoch_time() - self.initial_time]

            vehicle_csv_file = os.path.join(self.sim_mobility_output, f'{vehid}.csv')

            with open(vehicle_csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)


def arguments():
    parser = argparse.ArgumentParser(description='Required arguments to run SUMO simulations')
    parser.add_argument('--scenario_path', type=str, default='2023-07-13-15-23-35', help='The relative path of the '
                                                                                         'scenario')
    return parser.parse_args()


def abs_path(path):
    return os.path.join(os.path.normpath(os.getcwd()), path)
