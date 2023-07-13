from components.simulation import Simulation, arguments

scenario_path = arguments().scenario_path

Simulation(scenario_path).run()
