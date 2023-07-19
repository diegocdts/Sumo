import os
import csv
import time
import argparse
import traci

from datetime import datetime


class Simulation:
    def __init__(self, scenario_path, simulation_time, window_size):
        """
        Instantiates and starts a simulation, exporting raw mobility data of each moving object to its respective file.
        It creates one directory for each simulation round, identified by yyyy-mm-dd-H-M-S
        """
        self.scenario_path = scenario_path
        self.trace_path = f'{self.scenario_path}/sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'

        if not os.path.exists(self.trace_path):
            os.makedirs(self.trace_path)

        self.simulation_time = simulation_time
        self.window_size = window_size

        self.sumoCmd = ['sumo', '-c', f'{self.scenario_path}/osm.sumocfg']
        self.run()

    def run(self):
        """
        runs a simulation
        """
        traci.start(self.sumoCmd)

        current_window = 0

        while traci.simulation.getMinExpectedNumber() > 0 and traci.simulation.getTime() < self.simulation_time:
            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()

            if traci.simulation.getTime() % self.window_size == 0:
                current_window += 1

            self.write_trace(vehicles, current_window)

        traci.close()
        time.sleep(5)

    def write_trace(self, vehicles, current_window):
        """
        writes the current position of a moving object in its respective simulation file
        :param vehicles: the vehicles moving
        """
        for i in range(0, len(vehicles)):
            vehid = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicles[i])

            record = [current_window, x, y, traci.simulation.getTime()]

            vehicle_csv_file = os.path.join(self.trace_path, f'{vehid}.csv')

            with open(vehicle_csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)


def arguments():
    parser = argparse.ArgumentParser(description='Required arguments to run SUMO simulations')
    parser.add_argument('--scenario_path', type=str, default='2023-07-13-15-23-35', help='The relative path of the '
                                                                                         'scenario')
    parser.add_argument('--simulation_time', type=int, default='7200', help='The simulation time duration')
    parser.add_argument('--window_size', type=int, default='60', help='The time window size to generate mobility '
                                                                     'samples')
    return parser.parse_args()
