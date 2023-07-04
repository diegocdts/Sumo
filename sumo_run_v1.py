import csv
import os
import time
import traci

from datetime import datetime


def exists_path(name):
    if not os.path.exists(name):
        os.makedirs(name)


def get_datetime():
    epoch_time = int(time.time())
    return epoch_time


def flatten_list(_2d_list):
    flat_list = []
    for element in _2d_list:
        if type(element) is list:
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


sumoCmd = ['sumo', '-c', 'osm.sumocfg']
traci.start(sumoCmd)

directory = f'sim_{datetime.now().strftime("%y-%m-%d-%H-%M-%S")}'
exists_path(directory)

while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    for i in range(0, len(vehicles)):
        vehid = vehicles[i]
        x, y = traci.vehicle.getPosition(vehicles[i])
        lon, lat = traci.simulation.convertGeo(x, y)

        record = [lat, lon, get_datetime()]

        vehicle_file = os.path.join(directory, f'{vehid}.csv')

        with open(vehicle_file, 'a', newline='') as file_csv:
            writer = csv.writer(file_csv)
            writer.writerow(record)


traci.close()
time.sleep(5)
