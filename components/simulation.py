import os
import time
import traci
import re

from components.settings import SimulationSettings


def id_dict(key):
    conditions = {
        'bik': 1000,
        'bus': 2000,
        'mot': 3000,
        'ped': 4000,
        'tru': 5000,
        'veh': 6000
    }
    return conditions.get(key[:3])


def replace_id(id_key):
    code_id = id_dict(id_key)  # get the code of a moving object
    digit_index = re.search(r'\d', id_key).start()  # find the index position to cut the id
    new_id = f'{code_id}{id_key[digit_index:]}'  # form the new id
    return new_id


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

        one_trace = os.path.join(self.settings.trace_path, 'one_trace.txt')

        while traci.simulation.getMinExpectedNumber() > 0:

            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()
            people = traci.person.getIDList()

            self.write_trace(vehicles, people, one_trace)
            print(traci.simulation.getTime())

        traci.close()
        time.sleep(5)

    def write_trace(self, vehicles=None, people=None, one_trace=''):
        """
        writes the current position of each user in its respective simulation file
        :param vehicles: list of vehicles
        :param people: list of people
        :param one_trace: path to the ns trace file
        """

        timestamp = int(traci.simulation.getTime())

        for i in range(0, len(vehicles)):
            vehicle_id = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicle_id)

            x, y = round(x, 2), round(y, 2)
            speed = round(traci.vehicle.getSpeed(vehicle_id), 2)

            raw_record = f'{x}, {y}, {timestamp}\n'
            one_record = f'{timestamp} {replace_id(vehicle_id)} {x} {y}\n'

            raw_file = os.path.join(self.settings.trace_path, f'{vehicle_id}.csv')

            with open(raw_file, 'a', newline='') as vehicle_file:
                vehicle_file.write(raw_record)

            with open(one_trace, 'a', newline='') as one_file:
                one_file.write(one_record)

        for i in range(0, len(people)):
            person_id = people[i]
            x, y = traci.person.getPosition(person_id)

            x, y = round(x, 2), round(y, 2)
            speed = round(traci.person.getSpeed(person_id), 2)

            raw_record = f'{x}, {y}, {int(traci.simulation.getTime())}\n'
            one_record = f'{timestamp} {replace_id(person_id)} {x} {y}\n'

            raw_file = os.path.join(self.settings.trace_path, f'{person_id}.csv')

            with open(raw_file, 'a', newline='') as person_file:
                person_file.write(raw_record)

            with open(one_trace, 'a', newline='') as one_file:
                one_file.write(one_record)
