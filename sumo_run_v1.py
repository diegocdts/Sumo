from components.simulation import Simulation, arguments

args = arguments()
scenario_path = args.scenario_path
simulation_time = args.simulation_time

Simulation(scenario_path, simulation_time)
