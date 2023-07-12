import csv
import os
import time

import traci
from datetime import datetime


class SimRecorder:
    def __init__(self):
        """
        Instantiates a simulation recorder to export raw mobility data from each moving object to its respective file.
        It creates one directory for each simulation round, identified by yyyy-mm-dd-H-M-S
        """
        self.sim_path = f'sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'
        if not os.path.exists(self.sim_path):
            os.makedirs(self.sim_path)

    def get_epoch_time(self):
        """
        :return: the current epoch time
        """
        epoch_time = int(time.time())
        return epoch_time

    def write_trace(self, vehicles):
        """
        writes the current position of a moving object in its respective simulation file
        :param vehicles: the vehicles moving
        """
        for i in range(0, len(vehicles)):
            vehid = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicles[i])
            lon, lat = traci.simulation.convertGeo(x, y)

            record = [lat, lon, self.get_epoch_time()]

            vehicle_csv_file = os.path.join(self.sim_path, f'{vehid}.csv')

            with open(vehicle_csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)