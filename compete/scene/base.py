from typing import List

from ..config import Configurable
from ..message import Message
from ..agent import Player
from ..globals import NAME2PORT, DELIMITER
from ..utils import PromptTemplate, send_data_to_database, get_data_from_database

import re
import os
import json


class Scene(Configurable):
    def __init__(self, players: List[Player], type_name: str, **kwargs):
        """
        Initialize a scene
        
        Parameters:
            message_pool (MessagePool): The message pool for the scene
            players (List[Player]): The players in the scene
        """
        super().__init__(players=players, type_name=type_name, **kwargs)
        self.players = players
        self.log_path = None
        
        self.num_of_players = len(players)
        self.invalid_step_retry = 3
        
        self._curr_turn = 0  
        self._curr_player_idx = 0
        self._curr_process_idx = 0
    
    def add_new_prompt(self, player_name, scene_name=None, step_name=None, data=None, from_db=False):
        prompt = None
        if scene_name and step_name:
            if PromptTemplate([scene_name, step_name]).content:
                prompt_template = PromptTemplate([scene_name, step_name])
                if from_db:
                    data = get_data_from_database(step_name, NAME2PORT[player_name])
                    data = str(data)
                prompt = prompt_template.render(data=data)
        elif isinstance(data, str) and data != "None":
            prompt = data
        else:
            raise ValueError("Prompt not found")

        message = Message(agent_name='System', content=prompt, 
                            visible_to=player_name, turn=self._curr_turn)
        self.message_pool.append_message(message)
    
    def parse_output(self, output, player_name, step_name, to_db=False):  

        if to_db and output != 'None':
            try:
                send_data_to_database(output, step_name, NAME2PORT[player_name])
            except Exception as e:
                raise Exception(f"Send data to database: {step_name} {NAME2PORT[player_name]} {e}")

        index = min(output.find("["), output.find("{"))
        if index != -1:
            output = output[index:]
            
        try:
            json_output = json.loads(output)
        except:
            json_output = None                    
                    
        def shorten_text(text):
            delimiter_idx = text.find(DELIMITER)
            if delimiter_idx != -1:
                return text[:delimiter_idx].strip()
            else:
                return text
            
        last_message = self.message_pool.get_last_message_system_to_player(player_name)
        if last_message:
            last_message.content = shorten_text(last_message.content)
            
        message = Message(agent_name=player_name, content=output, 
                            visible_to="all", turn=self._curr_turn)
        self.message_pool.append_message(message)
        
        return json_output
    
    @classmethod
    def action_for_next_scene(self, data):
        return
            
    def is_terminal(self):
        pass
    
    def terminal_action(self):
        pass
    
    def get_curr_player(self):
        return self.players[self._curr_player_idx]
    
    def get_curr_process(self):
        return self.processes[self._curr_process_idx]
        
    def step(self, data=None):
        pass

    def run(self, previous_scene_data=None):
        """
        Main function, automatically assemble input and parse output to run the scene
        """
        data = previous_scene_data
        while not self.is_terminal():
            data = self.step(data)
        
        self.terminal_action()
        
        return data