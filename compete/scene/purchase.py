from typing import List
from .base import Scene
from ..agent import Player
from ..message import MessagePool
from ..globals import NAME2PORT, PORT2NAME
from ..utils import log_table, get_data_from_database, send_data_to_database

import numpy as np
     
EXP_NAME = None

processes = [
    {"name": "order", "from_db": False, "to_db": False},
    {"name": "comment", "from_db": False, "to_db": False},
    {"name": "feeling", "from_db": False, "to_db": False},
]

class Purchase(Scene):
    
    type_name = "purchase"
    
    def __init__(self, players: List[Player], id: int, exp_name: str, **kwargs):
        super().__init__(players=players, id=id, type_name=self.type_name, **kwargs)
        
        global EXP_NAME
        EXP_NAME = exp_name
        
        self.processes = processes
        self.log_path = f"./logs/{exp_name}/{self.type_name}_{id}"
        self.message_pool = MessagePool(log_path=self.log_path)
        
        self.month = 1
        self.products = None
        self.terminal_flag = False
    
    @classmethod
    def action_for_next_scene(cls, data):
        company_list = []
        daybooks = {}
        comments = {}
        num_of_customer = {}
        infos = {}
        rival_infos = {}
        customer_choice = {}

        for value in PORT2NAME.values():
            company_list.append(value)
            comments[value] = []
            daybooks[value] = {}
            num_of_customer[value] = 0
            infos[value] = ''
            rival_infos[value] = ''
            
        month = None
        for d in data:
            agent_name = next(iter(d))
            d = d[agent_name]
            
            c_name = d["company"]
            customer_choice[agent_name] = c_name
            
            if c_name == 'None':
                continue
            
            if month is None:
                month = d["month"]
            
            if "comment" in d:
                comment = {"month": d["month"], "name": agent_name, "score": d["score"], "content":  d["comment"]}
                comments[c_name].append({"type": "add", "data": comment})
              
            products = d["products"]
            num_of_customer[c_name] += 1
            for product in products:
                if not product in daybooks[c_name]:
                    daybooks[c_name][product] = 0
                daybooks[c_name][product] += 1
                
        if month is None:
            month = 1  # Default to month 1 if no valid data is found
                
        log_path = f'./logs/{EXP_NAME}/{cls.type_name}'
        log_table(log_path, customer_choice, f"month{month}")


        for key in comments:
            send_data_to_database(comments[key], "comment", port=NAME2PORT[key])
        
        for c_name in company_list:
            show = get_data_from_database("show", port=NAME2PORT[c_name])
            info = f"Company: {c_name} \nNumber of customers: {num_of_customer[c_name]}\n Customer Comments: {show['comment']} \nMenu: {show['menu']}\n "
            infos[c_name] = info
        
        for key in daybooks:
            for c_name in company_list:
                if c_name != key:
                    rival_infos[key] += infos[c_name]
            daybook = {"products": daybooks[key], "num_of_customer": num_of_customer[key], "rival_info": rival_infos[key]}
            
            print(f'debugging-daybook: {daybook}')
            
            daybooks[key] = {"type": "add", "data": daybook}

        for key in daybooks:
            send_data_to_database(daybooks[key], "daybook", port=NAME2PORT[key])
        
        return
        
    def is_terminal(self):
        return self.terminal_flag

    def terminal_action(self):
        self.month += 1
        self._curr_process_idx = 0
        self.terminal_flag = False
        
        self.message_pool.remove_role_messages(role="System")
    
    def move_to_next_player(self):
        self._curr_player_idx = 0
    
    def move_to_next_process(self):
        if self._curr_process_idx == 0:
            self._curr_process_idx += np.random.choice([1, 2], p=[0.3, 0.7])
        else:
            self.terminal_flag = True
    
    def prepare_for_next_step(self):
        self.move_to_next_player()
        self.move_to_next_process()
        self._curr_turn += 1
    
    def step(self, input=None):
        curr_player = self.get_curr_player()
        curr_process = self.get_curr_process()
        result = None
        
        if curr_process['name'] == 'order':
            for k in input.keys():
                if k in input and isinstance(input[k], dict) and 'today_offering' in input[k]:
                    self.add_new_prompt(player_name=curr_player.name, 
                                data=input[k]['today_offering'])
                else:
                    self.add_new_prompt(player_name=curr_player.name, 
                                data=None)
            self.add_new_prompt(player_name=curr_player.name, 
                                scene_name=self.type_name, 
                                step_name=curr_process['name'], 
                                from_db=curr_process['from_db'])
        elif curr_process['name'] in ('comment', 'feeling'):
            self.add_new_prompt(player_name=curr_player.name,
                                scene_name=self.type_name,
                                step_name=curr_process['name'],
                                data=input)

        observation_text = self.message_pool.get_visible_messages(agent_name=curr_player.name, turn=self._curr_turn)
        
        parsed_ouput = None
        for i in range(self.invalid_step_retry):
            try:
                output = curr_player(observation_text)
                if not output or output == 'None':
                    raise ValueError("Empty or None output received")
                    
                parsed_ouput = self.parse_output(output, curr_player.name, curr_process['name'], curr_process['to_db'])
                if not parsed_ouput:
                    raise ValueError("Failed to parse output as valid JSON")
                    
                if curr_process['name'] in ('comment', 'feeling') and not isinstance(parsed_ouput.get('data', {}), dict):
                    raise ValueError("Invalid output format for comment/feeling - data must be a JSON object")
                    
                break
            except Exception as e:
                logging.error(f"Attempt {i + 1} failed with error: {e}")
                if i == self.invalid_step_retry - 1:
                    if curr_process['name'] == 'order':
                        return {self.players[0].name: {'company': 'None'}}
                    raise RuntimeError(f"Maximum retry attempts reached: {str(e)}")

        
        if curr_process['name'] == 'order':
            company = parsed_ouput['company']
            if company not in input.keys() or company == 'None':
                result = {self.players[0].name: {'company': 'None'}}
                self.terminal_flag = True
                return result
            self.products = parsed_ouput['products']
            product_score = input[company]['product_score']
            
            prompt = ''
            for product in self.products:
                if product in product_score.keys():
                    score = product_score[product]
                    prompt += f"\n{product}: {score}"
                result = prompt
        
        if curr_process['name'] in ('comment', 'feeling'):
            purchase_info = parsed_ouput
            purchase_info['products'] = self.products
            purchase_info['month'] = self.month
            customer_name = self.players[0].name
            purchase_info = {customer_name: purchase_info}
            result = purchase_info
                
        self.prepare_for_next_step()
        
        return result