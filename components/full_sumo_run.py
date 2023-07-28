import traci
import time
from random import randrange
import pandas as pd


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
    traffic_lights = traci.trafficlight.getIDList()

    for i in range(0, len(vehicles)):

        # Function descriptions
        # https://sumo.dlr.de/docs/TraCI/Vehicle_Value_Retrieval.html
        # https://sumo.dlr.de/pydoc/traci._vehicle.html#VehicleDomain-getSpeed
        vehid = vehicles[i]
        x, y = traci.vehicle.getPosition(vehicles[i])
        coord = [x, y]
        lon, lat = traci.simulation.convertGeo(x, y)
        gps_coord = [lon, lat]
        spd = round(traci.vehicle.getSpeed(vehicles[i]) * 3.6, 2)
        edge = traci.vehicle.getRoadID(vehicles[i])
        lane = traci.vehicle.getLaneID(vehicles[i])
        displacement = round(traci.vehicle.getDistance(vehicles[i]), 2)
        turnAngle = round(traci.vehicle.getAngle(vehicles[i]), 2)
        nextTLS = traci.vehicle.getNextTLS(vehicles[i])

        # Packing of all the data for export to CSV/XLSX
        vehList = [get_datetime(), vehid, coord, gps_coord, spd, edge, lane, displacement, turnAngle, nextTLS]

        print('Vehicle: ', vehicles[i], ' at datetime: ', get_datetime())
        print(vehicles[i], ' >>> Position: ', coord, ' | GPS Position: ', gps_coord, ' |',
              ' Speed: ', round(traci.vehicle.getSpeed(vehicles[i]) * 3.6, 2), 'km/h |',
              # Returns the id of the edge the named vehicle was at within the last step.
              ' EdgeID of veh: ', traci.vehicle.getRoadID(vehicles[i]), ' |',
              # Returns the id of the lane the named vehicle was at within the last step.
              ' LaneID of veh: ', traci.vehicle.getLaneID(vehicles[i]), ' |',
              # Returns the distance to the starting point like an odometer.
              ' Distance: ', round(traci.vehicle.getDistance(vehicles[i]), 2), 'm |',
              # Returns the angle in degrees of the named vehicle within the last step.
              ' Vehicle orientation: ', round(traci.vehicle.getAngle(vehicles[i]), 2), 'deg |',
              # Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
              ' Upcoming traffic lights: ', traci.vehicle.getNextTLS(vehicles[i]),
              )

        idd = traci.vehicle.getLaneID(vehicles[i])

        tlsList = []

        for k in range(0, len(traffic_lights)):

            # Function descriptions
            # https://sumo.dlr.de/docs/TraCI/Traffic_Lights_Value_Retrieval.html#structure_of_compound_object_controlled_links
            # https://sumo.dlr.de/pydoc/traci._trafficlight.html#TrafficLightDomain-setRedYellowGreenState

            if idd in traci.trafficlight.getControlledLanes(traffic_lights[k]):
                tf_light = traffic_lights[k]
                tl_state = traci.trafficlight.getRedYellowGreenState(traffic_lights[k])
                tl_phase_duration = traci.trafficlight.getPhaseDuration(traffic_lights[k])
                tl_lanes_controlled = traci.trafficlight.getControlledLanes(traffic_lights[k])
                tl_program = traci.trafficlight.getCompleteRedYellowGreenDefinition(traffic_lights[k])
                tl_next_switch = traci.trafficlight.getNextSwitch(traffic_lights[k])

                # Packing of all the data for export to CSV/XLSX
                tlsList = [tf_light, tl_state, tl_phase_duration, tl_lanes_controlled, tl_program, tl_next_switch]

                print(traffic_lights[k], ' --->',
                      # Returns the named tl's state as a tuple of light definitions from rRgGyYoO, for red,
                      # green, yellow, off, where lower case letters mean that the stream has to decelerate
                      ' TL state: ', traci.trafficlight.getRedYellowGreenState(traffic_lights[k]), ' |'
                      # Returns the default total duration of the currently active phase in seconds To obtain the
                      # remaining duration use (getNextSwitch() - simulation.getTime()) to obtain the spent duration
                      # subtract the remaining from the total duration
                      ' TLS phase duration: ', traci.trafficlight.getPhaseDuration(traffic_lights[k]), ' |'
                      # Returns the list of lanes which are controlled by the named traffic light. Returns at least
                      # one entry for every element of the phase state (signal index)                                
                      ' Lanes controlled: ', traci.trafficlight.getControlledLanes(traffic_lights[k]), ' |',
                      # Returns the complete traffic light program, structure described under data types
                      ' TLS Program: ', traci.trafficlight.getCompleteRedYellowGreenDefinition(traffic_lights[k]), ' |'
                      # Returns the assumed time (in seconds) at which the tls changes the phase. Please note that
                      # the time to switch is not relative to current simulation step (the result returned by the query
                      # will be absolute time, counting from simulation start)
                      # to obtain relative time, one needs to subtract current simulation time from the
                      # result returned by this query. Please also note that the time may vary in the case of
                      # actuated/adaptive traffic lights
                      ' Next TLS switch: ', traci.trafficlight.getNextSwitch(traffic_lights[k]))

        # Pack Simulated Data
        packBigDataLine = flatten_list([vehList, tlsList])
        packBigData.append(packBigDataLine)

        # ----------MACHINE LEARNING CODES/FUNCTIONS HERE---------- #

        # --------------------------------------------------------------- #

        # ----------CONTROL Vehicles and Traffic Lights---------- #

        # ***SET FUNCTION FOR VEHICLES***
        # REF: https://sumo.dlr.de/docs/TraCI/Change_Vehicle_State.html
        new_speed = 15  # value in m/s (15 m/s = 54 km/hr)
        if vehicles[i] == 'veh2':
            traci.vehicle.setSpeedMode('veh2', 0)
            traci.vehicle.setSpeed('veh2', new_speed)

        # ***SET FUNCTION FOR TRAFFIC LIGHTS***
        # REF: https://sumo.dlr.de/docs/TraCI/Change_Traffic_Lights_State.html
        traffic_light_duration = [5, 37, 5, 35, 6, 3]
        traffic_signal = ['rrrrrrGGGGgGGGrr', 'yyyyyyyyrrrrrrrr', 'rrrrrGGGGGGrrrrr', 'rrrrryyyyyyrrrrr', 
                          'GrrrrrrrrrrGGGGg', 'yrrrrrrrrrryyyyy']
        tfl = 'cluster_4260917315_5146794610_5146796923_5146796930_5704674780_5704674783_5704674784_5704674787_' \
              '6589790747_8370171128_8370171143_8427766841_8427766842_8427766845'
        traci.trafficlight.setPhaseDuration(tfl, traffic_light_duration[randrange(6)])
        traci.trafficlight.setRedYellowGreenState(tfl, traffic_signal[randrange(6)])

        # ------------------------------------------------------ #

traci.close()

# Generate Excel file
column_names = ['dateandtime', 'vehid', 'coord', 'gps_coord', 'spd', 'edge', 'lane', 'displacement', 'turnAngle',
                'nextTLS',
                'tf_light', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset = pd.DataFrame(packBigData, index=None, columns=column_names)
dataset.to_excel('output.xlsx', index=False)
time.sleep(5)
