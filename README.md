# Sumo
Projects developed in the SUMO urban mobility simulator

## Osm Web Wizard

To open the Osm Web Wizard, run the command bellow:

```bash
cd /usr/share/sumo/tools/
python osmWebWizard.py
```

## Netedit

To open the Netedit tool, run the command bellow:

```bash
cd /usr/share/sumo/bin/
netedit
```

## sumo_run.py

The sumo_run.py script simulates scenarios and GET simulation information, apply some custom machine learning method and SET new simulation
data.

## Arguments

The sumo_run.py may receive the following arguments:

* --scenario_path (mandatory): the name of the directory that includes the scenario simulation files
* --simulation_time: the maximum simulation time
* --temporal_resolution: the interval to generate a new sample
* --spatial_resolution: both width and height size of the cells
* --window_size: the quantity of intervals to be used for model training
* --max_communities: max number of communities the users may be clusted into
