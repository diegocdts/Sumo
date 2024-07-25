import os
import sys
import time
import traci
import re

from components.settings import SimulationSettings


class Simulation:
    def __init__(self, settings: SimulationSettings):
        """
        Instantiates and starts a simulation, exporting raw mobility data of each moving object to its respective file.
        It creates one directory for each simulation round, identified by yyyy-mm-dd-H-M-S
        :param settings a SimulationSettings object that contains all relevant information for the mobility simulation
        """
        self.settings = settings

        self.run()

    def run(self):
        traci.start(self.settings.sumoCmd)

        one_trace_path = os.path.join(self.settings.trace_path, 'one_trace.txt')

        dict_offset = {
            'min_time': sys.maxsize,
            'max_time': 0,
            'min_x': sys.maxsize,
            'max_x': 0,
            'min_y': sys.maxsize,
            'max_y': 0
        }

        while traci.simulation.getMinExpectedNumber() > 0:

            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()
            people = traci.person.getIDList()

            dict_offset = self.write_trace(vehicles, people, one_trace_path, dict_offset)
            print(traci.simulation.getTime())

        write_offset(one_trace_path, dict_offset)
        traci.close()
        time.sleep(5)

    def write_trace(self, vehicles=None, people=None, one_trace_path='', dict_offset=None):
        """
        writes the current position of each user in its respective simulation file
        :param vehicles: list of vehicles
        :param people: list of people
        :param one_trace_path: path to the ns trace file
        :param dict_offset: offset for the ONE trace
        """

        users = vehicles + people

        timestamp = int(traci.simulation.getTime())

        for index in range(0, len(users)):
            id = users[index]
            if index <= len(vehicles) - 1:
                x, y = traci.vehicle.getPosition(id)
            else:
                x, y = traci.person.getPosition(id)

            x, y = round(x, 2), round(y, 2)
            raw_record = f'{int(x)}, {int(y)}, {timestamp}\n'
            one_record = f'{timestamp} {index} {int(x)} {int(y)}\n'

            raw_file = os.path.join(self.settings.trace_path, f'user{index}.csv')

            with open(raw_file, 'a', newline='') as file:
                file.write(raw_record)

            with open(one_trace_path, 'a', newline='') as one_file:
                one_file.write(one_record)

            dict_offset = check_offset(dict_offset, timestamp, x, y)
        return dict_offset


def check_offset(dict_offset, timestamp, x, y):
    if timestamp < dict_offset.get('min_time'):
        dict_offset['min_time'] = timestamp

    if timestamp > dict_offset.get('max_time'):
        dict_offset['max_time'] = timestamp

    if x < dict_offset.get('min_x'):
        dict_offset['min_x'] = x

    if x > dict_offset.get('max_x'):
        dict_offset['max_x'] = x

    if y < dict_offset.get('min_y'):
        dict_offset['min_y'] = y

    if y > dict_offset.get('max_y'):
        dict_offset['max_y'] = y

    return dict_offset


def write_offset(one_trace_path, dict_offset):
    with open(one_trace_path, 'r') as file:
        lines = file.readlines()

    offset = (f'{dict_offset.get("min_time")} {dict_offset.get("max_time")} '
              f'{dict_offset.get("min_x")} {dict_offset.get("max_x")} '
              f'{dict_offset.get("min_y")} {dict_offset.get("max_y")} '
              f'0.0 0.0')

    lines.insert(0, offset + '\n')

    with open(one_trace_path, 'w') as file:
        file.writelines(lines)
