# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Competeai GitHub Repository: https://github.dev/microsoft/competeai

from compete.simul import Simulation
from compete.utils import analysis, aggregate

import os
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('name', type=str)
args = parser.parse_args()

log_path = f"./logs/{args.name}"

if not os.path.exists(log_path):
    os.makedirs(log_path)
    os.makedirs(f"{log_path}/fig")

config_path = os.path.join('compete', 'examples', 'descriptions.yaml')

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    config['exp_name'] = args.name
    Simul = Simulation.from_config(config)
    Simul.run()
    