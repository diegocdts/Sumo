from components.simulation import Simulation, arguments

args = arguments()
scenario_path = args.scenario_path
simulation_time = args.simulation_time
window_size = args.window_size

Simulation(scenario_path, simulation_time, window_size)
