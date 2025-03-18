# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Competeai GitHub Repository: https://github.dev/microsoft/competeai

from dataclasses import dataclass
from typing import Union, List
from concurrent.futures import ThreadPoolExecutor

from .config import SimulConfig
from .agent import Player
from .scene import load_scene, Scene

from .globals import NAME2PORT

class Simulation:
    def __init__(self, scenes: List[Scene]):
        self.scenes = scenes   
        self.curr_scene_idx = 0

    def get_curr_scene(self):
        return self.scenes[self.curr_scene_idx]
    
    def step(self, data):
        """
        Run one step of the simulation
        """
        current_scene = self.get_curr_scene()

        max_number_parallel = 3
        with ThreadPoolExecutor(max_workers=max_number_parallel) as executor:
            futures = [executor.submit(lambda s=scene: s.run(data)) for scene in current_scene]
            results = [future.result() for future in futures]
        next_scene_data = current_scene[0].action_for_next_scene(results)

        self.curr_scene_idx = (self.curr_scene_idx + 1) % len(self.scenes)
        
        return next_scene_data
    
    def run(self):
        """
        Main function, run the simulation
        """
        max_month = 15
        previous_scene_data = None
        
        i = 1
        while i <= len(self.scenes) * max_month + 1:
            i += 1
            data = self.step(previous_scene_data)
            previous_scene_data = data
    
    @classmethod
    def from_config(cls, config: Union[str, dict, SimulConfig]):
        """
        create an simul from a config
        """
        if isinstance(config, str):
            config = SimulConfig.load(config)
        if isinstance(config, dict):
            config = SimulConfig(config)

        global_prompt = config.get("global_prompt", None)
        database_port = config.get("database_port_base", None)
        exp_name = config.get("exp_name", None)

        # fill the port map, not a universal code  
        for scene_config in config.scenes:
            if scene_config['scene_type'] == 'strategy':
                for player in scene_config['players']:
                    NAME2PORT[player] = database_port
                    database_port += 1
        
        # Create the players
        # Add relationship!
        players = []
        for player_config in config.players:
            # Add public_prompt to the player config
            if global_prompt is not None:
                player_config["global_prompt"] = global_prompt
            player = Player.from_config(player_config)
            players.append(player)

        # Check that the player names are unique
        player_names = [player.name for player in players]
        assert len(player_names) == len(set(player_names)), "Player names must be unique"

        # Create scenes and decide their order
        scenes = []
        for scene_config in config.scenes:
            same_scene = []
            scene_config['exp_name'] = exp_name
            for i, player in enumerate(scene_config['players']):   
                scene_config['id'] = i
                # a single player or a group of players
                if isinstance(player, str):
                    assert player in player_names, f"Player {player} is not defined"
                    scene_config["players"] = [players[player_names.index(player)]]
                    scene = load_scene(scene_config)
                same_scene.append(scene)
            scenes.append(same_scene)
        return cls(scenes)