import os
import sys
import time
import traci

# the three lines bellow are responsible for adding the parent directory to the sys.path
# and import modules from different directories.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, "..")
sys.path.append(parent_dir)

from components.sim_recorder import SimRecorder

sumoCmd = ['sumo', '-c', 'osm.sumocfg']
traci.start(sumoCmd)

recorder = SimRecorder()

while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    recorder.write_trace(vehicles)

traci.close()
time.sleep(5)
