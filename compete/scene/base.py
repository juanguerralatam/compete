from typing import List

from ..config import Configurable
from ..message import Message
from ..agent import Player
from ..globals import NAME2PORT, DELIMITER
from ..utils import PromptTemplate, send_data_to_database, get_data_from_database

import re
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)

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
            prompt_path = os.path.join('prompt', scene_name, step_name + '.txt')
            logging.debug(f"Looking for prompt template at: {prompt_path}")
            if PromptTemplate([scene_name, step_name]).content:
                prompt_template = PromptTemplate([scene_name, step_name])
                if from_db:
                    data = get_data_from_database(step_name, NAME2PORT[player_name])
                    data = str(data)
                prompt = prompt_template.render(data=data)
            else:
                logging.debug(f"Prompt template not found at: {prompt_path}")
        elif isinstance(data, str) and data != "None":
            prompt = data
        else:
            logging.debug(f"No prompt found for {scene_name}/{step_name}")
            prompt = ""

        # Create a properly formatted Message object with required attributes
        message = Message(agent_name='System', content=prompt, 
                        visible_to=player_name, turn=self._curr_turn)
        message.agent_name = 'System'  # Ensure agent_name is set
        message.content = prompt       # Ensure content is set
        self.message_pool.append_message(message)

        message = Message(agent_name='System', content=prompt, 
                            visible_to=player_name, turn=self._curr_turn)
        self.message_pool.append_message(message)
    
    def parse_output(self, output, player_name, step_name, to_db=False):
        # Add empty response check
        if not output or not isinstance(output, str):
            logging.error(f"Empty output from {player_name}")
            return None
            
        # Clean potential markdown code blocks
        cleaned_output = output.replace('```json', '').replace('```', '').strip()
        
        try:
            # Validate JSON structure
            data = json.loads(cleaned_output)
            
            # Add required field validation
            if 'type' not in data or 'data' not in data:
                raise ValueError("Missing required fields 'type' or 'data'")
                
            # Find the first occurrence of JSON-like structure
            json_start = -1
            json_chars = ['{', '[']
            for char in json_chars:
                pos = output.find(char)
                if pos != -1 and (json_start == -1 or pos < json_start):
                    json_start = pos
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {e}\nRaw output: {output}")
            return None
        except ValueError as e:
            logging.error(f"Validation error: {e}")
            return None

        # Clean and validate output
        output = output.strip()
        if output.lower() == 'none':
            message = Message(agent_name=player_name, content="Empty response received", 
                            visible_to="all", turn=self._curr_turn)
            self.message_pool.append_message(message)
            return None

        # Find and parse JSON structure
        try:
            # Find the first occurrence of JSON-like structure
            json_start = -1
            json_chars = ['{', '[']
            for char in json_chars:
                pos = output.find(char)
                if pos != -1 and (json_start == -1 or pos < json_start):
                    json_start = pos

            if json_start != -1:
                output = output[json_start:]
            
            # Attempt to parse JSON and validate structure
            json_output = json.loads(output)
            
            # Validate JSON structure has required fields
            if not isinstance(json_output, dict):
                raise ValueError("Response must be a JSON object")
            if 'type' not in json_output or 'data' not in json_output:
                raise ValueError("Response must have 'type' and 'data' fields")
            if not isinstance(json_output['data'], dict):
                raise ValueError("The 'data' field must be a JSON object")

            # Send to database if required
            if to_db and json_output is not None:
                try:
                    port = NAME2PORT.get(player_name)
                    if not port:
                        raise ValueError(f"No port found for player {player_name}")
                    send_data_to_database(output, step_name, port)
                except Exception as e:
                    error_msg = f"Database error ({step_name}): {str(e)}"
                    message = Message(agent_name=player_name, content=error_msg,
                                    visible_to="all", turn=self._curr_turn)
                    self.message_pool.append_message(message)
                    return None

        except json.JSONDecodeError as e:
            json_output = None
            error_msg = f"Invalid JSON format: {str(e)}"
            message = Message(agent_name=player_name, content=error_msg,
                            visible_to="all", turn=self._curr_turn)
            self.message_pool.append_message(message)
        except Exception as e:
            json_output = None
            error_msg = f"Error processing output: {str(e)}"
            message = Message(agent_name=player_name, content=error_msg,
                            visible_to="all", turn=self._curr_turn)
            self.message_pool.append_message(message)
                    
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