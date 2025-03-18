from typing import List
from .base import Scene
from ..agent import Player
from ..message import MessagePool
from ..globals import NAME2PORT, PORT2NAME, BASE_PORT
from ..utils import PromptTemplate, get_data_from_database, log_table
import os 
import json                 
 
EXP_NAME = None
 
processes = [
    {"name": "plan", "from_db": False, "to_db": False},
    {"name": "basic_info", "from_db": True, "to_db": True},
    {"name": "portfolio", "from_db": True, "to_db": True},
    {"name": "deparment_rd", "from_db": True, "to_db": True},
    {"name": "deparment_mkt", "from_db": True, "to_db": True},
    {"name": "ads", "from_db": True, "to_db": True},
    {"name": "summary", "from_db": False, "to_db": False},
]

class Strategy(Scene):
    
    type_name = "strategy"
    
    def __init__(self, players: List[Player], id: int, exp_name: str, **kwargs):
        super().__init__(players=players, id=id, type_name=self.type_name, **kwargs)
        global EXP_NAME
        EXP_NAME = exp_name
        
        self.port = BASE_PORT + id
        
        # No longer initializing basic info here
        
        self.processes = processes
        
        self.log_path = f"./logs/{exp_name}/{self.type_name}_{self.port}"
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
            
        self.message_pool = MessagePool(log_path=f'{self.log_path}/message')
        
        self.month = 0
        
        for player in players:
            NAME2PORT[player.name] = self.port
    
    def is_terminal(self):
        return self._curr_process_idx == len(self.processes)
    
    def terminal_action(self):
        try:
            # Get basic info from database
            basic_info = get_data_from_database("basic_info", port=self.port)
            
            # Add null check before accessing list
            if not basic_info:
                print("No basic_info data found in database")
                return

            company_name = basic_info[0]["name"]
            NAME2PORT[company_name] = self.port
            PORT2NAME[self.port] = company_name
            
            if self.message_pool and self.message_pool.last_message:
                summary = self.message_pool.last_message
                summary.content = f"Month{self.month} summary: {summary.content}"
                self.message_pool.compress_last_turn(summary)
            
            self.month += 1
            self._curr_turn += 1
            self._curr_process_idx = 0
        except Exception as e:
            print(f"Error in terminal_action: {e}")
            return
    
    def action_for_next_scene(self, data=None):
        ports = set(NAME2PORT.values())
        res = {}

        for port in ports:
            try:
                data = get_data_from_database("show", port=self.port)
                if not data:
                    print(f"No data found for port {port}")
                    continue
                portfolio = data.get("portfolio", {})
                company = data.get("name", "Unknown")
                today_offering = PromptTemplate([self.type_name, "today_offering"]).render(data=data.values())
                product_score = get_data_from_database("score", port=port)
                res[company] = {"today_offering": today_offering, "product_score": product_score}
            except Exception as e:
                print(f"Error retrieving data for port {port}: {e}")
                continue
            
        return res
        
    def move_to_next_player(self):
        self._curr_player_idx = 0
    
    def move_to_next_process(self):
        self._curr_process_idx += 1
    
    def prepare_for_next_step(self):
        self.move_to_next_player()
        self.move_to_next_process()
    
    def step(self, input=None):
        curr_process = self.get_curr_process()
        curr_player = self.get_curr_player()
        
        if curr_process['name'] == 'plan' and self.month != 0:
            daybooks = get_data_from_database("daybook", port=self.port)
            
            rival_info = daybooks[self.month-1]["rival_info"]
            
            if len(daybooks) > 5:
                daybooks = daybooks[-5:]
            daybook_list = []
            for i, daybook in enumerate(daybooks):
                daybook = {k: v for k, v in daybook.items() if k != "rival_info"}
                daybook_list.append(daybook)
                
            comment = get_data_from_database("last_comment", port=self.port)
            portfolio = get_data_from_database("portfolio", port=self.port)
            portfolio = {'portfolio': json.dumps(portfolio)}
            
            data = [self.month, daybook_list, comment, rival_info] 
            
            self.add_new_prompt(player_name=curr_player.name, 
                                scene_name=self.type_name, 
                                step_name='daybook', 
                                data=data)
            log_table(f'{self.log_path}/data', daybook_list[-1], f"month{self.month}")
            log_table(f'{self.log_path}/portfolio', portfolio, f"month{self.month}")
            
        self.add_new_prompt(player_name=curr_player.name, 
                            scene_name=self.type_name, 
                            step_name=curr_process['name'], 
                            from_db=curr_process['from_db'])
        
        history = True if curr_process['name'] == 'plan' else False
        observation_text = self.message_pool.get_visible_messages(agent_name=curr_player.name, turn=self._curr_turn, history=history)
        for i in range(self.invalid_step_retry):
            try:
                output = curr_player(observation_text)
                self.parse_output(output, curr_player.name, curr_process['name'], curr_process['to_db'])
                break
            except Exception as e:
                print(f"Attempt {i + 1} failed with error: {e}")
        else:
            print("Invalid step retry arrived at maximum. Moving to the next step.")
        
        self.prepare_for_next_step()
        
        return