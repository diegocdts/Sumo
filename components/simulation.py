import gc
import os
import csv
import time
import argparse
import traci

from FLPUCI.model.clustering import GaussianMixtureModel
from FLPUCI.pre_processing.sample_generation import DisplacementMatrix
from FLPUCI.model.tf.federated_learning import FederatedFullConvolutionalAutoEncoder as ffcae
from FLPUCI.utils.props import FCAEProperties, TrainingParameters
from components.settings import SimulationSettings


class Simulation:
    def __init__(self, settings: SimulationSettings, parameters: TrainingParameters, properties: FCAEProperties):
        """
        Instantiates and starts a simulation, exporting raw mobility data of each moving object to its respective file.
        It creates one directory for each simulation round, identified by yyyy-mm-dd-H-M-S
        :param settings a SimulationSettings object that contains all relevant information for the mobility simulation
        :param parameters a TrainingParameters object
        :param properties a FCAEProperties object
        """
        self.settings = settings
        self.parameters = parameters
        self.properties = properties

        self.dm = DisplacementMatrix(settings)
        self.ffcae = None
        self.gmm = GaussianMixtureModel(settings.max_communities)

        self.current_interval = 0  # initiates the interval controller

        self.run()

    def run(self):
        """
        runs a mobility simulation
        """
        traci.start(self.settings.sumoCmd)

        while self.condition_to_run():

            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()

            if self.interval_changed():   # performs the computation when the interval changes

                self.dm.new_record(self.current_interval)
                self.federated_learning(self.current_interval)
                self.current_interval += 1

            self.write_trace(vehicles, self.current_interval)

        traci.close()
        time.sleep(5)

    def condition_to_run(self):
        """
        specifies the condition to run a mobility simulation
        :return: True if the traci.simulation.getTime() achieved the self.settings.simulation_time. False otherwise
        """
        return traci.simulation.getMinExpectedNumber() > 0 \
            and traci.simulation.getTime() < self.settings.simulation_time

    def interval_changed(self):
        """
        specifies the interval changing condition
        :return: True if traci.simulation.getTime() module self.settings.temporal_resolution equals zero.
        False otherwise
        """
        return traci.simulation.getTime() % self.settings.temporal_resolution == 0

    def write_trace(self, vehicles, current_interval):
        """
        writes the current position of a moving object in its respective simulation file
        :param vehicles: the moving vehicles
        :param current_interval: the current interval during simulation
        """
        for i in range(0, len(vehicles)):
            vehid = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicles[i])

            record = [current_interval, x, y, traci.simulation.getTime()]

            vehicle_csv_file = os.path.join(self.settings.trace_path, f'{vehid}.csv')

            with open(vehicle_csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)

    def federated_learning(self, current_interval: int):
        """
        performs federated model training and clusters the users of the current interval
        :param current_interval: the current interval
        """
        if current_interval >= self.settings.window_size:
            if not self.ffcae:
                self.ffcae = ffcae(self.settings, self.parameters, self.properties)

            self.ffcae.training(start_window=current_interval - self.settings.window_size, end_window=current_interval)
            predictions, indices = self.ffcae.encoder_prediction(start_window=current_interval,
                                                                 end_window=current_interval+1)
            clusters, labels = self.gmm.best_communities(predictions)
            gc.collect()


def arguments():
    """
    sets the required arguments to run SUMO simulations
    :return: the parsed arguments
    """
    parser = argparse.ArgumentParser(description='Required arguments to run SUMO simulations')
    parser.add_argument('--scenario_path', type=str, default='None', help='The relative path of the '
                                                                                         'scenario')
    parser.add_argument('--simulation_time', type=int, default=7200, help='The simulation time duration')
    parser.add_argument('--temporal_resolution', type=int, default=120, help='The interval to generate mobility '
                                                                             'samples')
    parser.add_argument('--spatial_resolution', type=int, default=150, help='The cell resolution')
    parser.add_argument('--window_size', type=int, default=4, help='The number of intervals inside a window')
    parser.add_argument('--max_communities', type=int, default=10, help='The total number of communities to be tested '
                                                                        'by the GaussianMixtureModel')
    return parser.parse_args()
