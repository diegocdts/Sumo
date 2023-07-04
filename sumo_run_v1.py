import traci
import time
import pandas as pd


# TODO: change get_datatime to return epoch time
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

packVehicleData = []
packTLSData = []
packBigData = []

# TODO: save in file (one file per vehicle/user) the lat, lon and timestamp
# TODO: traffic light data??
while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()

    for i in range(0, len(vehicles)):

        # Function descriptions
        # https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
        # https://sumo.dlr.de/pydoc/traci._vehicle.html#VehicleDomain-getSpeed
        vehid = vehicles[i]
        x, y = traci.vehicle.getPosition(vehicles[i])
        lon, lat = traci.simulation.convertGeo(x, y)

        # Packing of all the data for export to CSV/XLSX
        vehicle_record = [lat, lon, get_datetime()]

        print('Vehicle: ', vehicles[i], ' at datetime: ', get_datetime())

        # Pack Simulated Data
        packBigDataLine = flatten_list(vehicle_record)
        packBigData.append(packBigDataLine)

        # ----------MACHINE LEARNING CODES/FUNCTIONS HERE---------- #

        # --------------------------------------------------------------- #

        # ----------CONTROL Vehicles and Traffic Lights---------- #

        # ***SET FUNCTION FOR VEHICLES***
        # REF: https://sumo.dlr.de/docs/TraCI/Change_Vehicle_State.html

traci.close()

# Generate Excel file
dataset = pd.DataFrame(packBigData)
dataset.to_csv('output.csv', index=False, header=False)
time.sleep(5)
