import os
import csv
import time
import traci

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

        while traci.simulation.getMinExpectedNumber() > 0:

            traci.simulationStep()

            vehicles = traci.vehicle.getIDList()
            people = traci.person.getIDList()

            self.write_trace(vehicles, people)
            print(traci.simulation.getTime())

        traci.close()
        time.sleep(5)

    def write_trace(self, vehicles=None, people=None):
        """
        writes the current position of each user in its respective simulation file
        :param vehicles: list of vehicles
        :param people: list of people
        """
        for i in range(0, len(vehicles)):
            vehicle_id = vehicles[i]
            x, y = traci.vehicle.getPosition(vehicles[i])

            record = [round(x, 2), round(y, 2), int(traci.simulation.getTime())]

            csv_file = os.path.join(self.settings.trace_path, f'{vehicle_id}.csv')

            with open(csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)

        for i in range(0, len(people)):
            person_id = people[i]
            x, y = traci.person.getPosition(people[i])

            record = [round(x, 2), round(y, 2), int(traci.simulation.getTime())]

            csv_file = os.path.join(self.settings.trace_path, f'{person_id}.csv')

            with open(csv_file, 'a', newline='') as file_csv:
                writer = csv.writer(file_csv)
                writer.writerow(record)
