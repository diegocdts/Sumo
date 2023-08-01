#!/bin/bash

sudo systemctl disable --now systemd-oomd

ulimit -n 1048576

source "venv/bin/activate"

python sumo_run.py --scenario_path $1