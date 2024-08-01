import os
import time
import traci

from components.handle_trace import handle
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

        while traci.simulation.getMinExpectedNumber() > 0 and traci.simulation.getTime() <= 3600:

            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()
            people = traci.person.getIDList()

            self.write_trace(vehicles, people, one_trace_path)
            print(traci.simulation.getTime())

        traci.close()
        time.sleep(5)
        handle(one_trace_path)

    def write_trace(self, vehicles=None, people=None, one_trace_path=''):
        """
        writes the current position of each user in its respective simulation file
        :param vehicles: list of vehicles
        :param people: list of people
        :param one_trace_path: path to the ns trace file
        """
        timestamp = int(traci.simulation.getTime())

        for index in range(0, len(vehicles)):
            user_id = vehicles[index]
            x, y = traci.vehicle.getPosition(user_id)

            x, y = round(x, 2), round(y, 2)
            raw_record = f'{int(x)}, {int(y)}, {index}, {timestamp}\n'
            one_record = f'{timestamp} {user_id} {int(x)} {int(y)}\n'

            raw_file = os.path.join(self.settings.trace_path, f'{user_id}.csv')

            with open(raw_file, 'a', newline='') as file:
                file.write(raw_record)

            with open(one_trace_path, 'a', newline='') as one_file:
                one_file.write(one_record)

        for index in range(0, len(people)):
            user_id = people[index]
            x, y = traci.person.getPosition(user_id)

            x, y = round(x, 2), round(y, 2)
            raw_record = f'{int(x)}, {int(y)}, {index}, {timestamp}\n'
            one_record = f'{timestamp} {user_id} {int(x)} {int(y)}\n'

            raw_file = os.path.join(self.settings.trace_path, f'{user_id}.csv')

            with open(raw_file, 'a', newline='') as file:
                file.write(raw_record)

            with open(one_trace_path, 'a', newline='') as one_file:
                one_file.write(one_record)
