#!/bin/bash
python "$SUMO_HOME/tools/randomTrips.py" -n osm.net.xml.gz --fringe-factor 2 --insertion-density 20 -o osm.pedestrian.trips.xml -r osm.pedestrian.rou.xml -b 0 -e 3600 --vehicle-class pedestrian --prefix ped --pedestrians --max-distance 2000
