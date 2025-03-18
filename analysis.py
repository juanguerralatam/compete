# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Competeai GitHub Repository: https://github.dev/microsoft/competeai

import os
import re
import time
import yaml
import multiprocessing
import requests
import json

prompt_template = """
You are outstanding data analysts. Now you need to analyze the reason of customer choices. Next is the thought process of customer:
{process}

This customer role description is 
{role_desc}

Please choose single or multi options:
1: Infrastructure Compatibility (Align with technical requirements and scalability needs)
2: Proven Reliability & SLAs (Track record of uptime and service-level agreements)
3: Industry Reputation & Peer Validation (Endorsements from telecom regulators or enterprise clients)
4: Cost Efficiency & ROI (Total cost of ownership vs. long-term ROI)
5: Proprietary Technology or Patents (Unique solutions like low-latency routing or energy-efficient hardware)
6: Future-Proof Innovation (Support for emerging tech like 5G, IoT, or edge computing)

Only output all answer (1 - 6)
"""


OLLAMA_API_URL = "http://localhost:11434/api/chat"

def get_gpt_response(prompt):
    payload = {
        "model": "qwen2.5",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    json_payload = json.dumps(payload)

    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
    response = response.strip()    
    time.sleep(5)
    return response


def single_reason(path='./logs'):

    with open('compete/examples/descriptions.yaml', 'r') as f:
        config = yaml.safe_load(f)

    players = config['players']
    players = players[2:]
    players_name = [ 'Jack', 'Xena', 'Bob']    

    player2idx = {}
    player2role = {}
    for i, player in enumerate(players):
        player2idx[player['name']] = i
        player2role[player['name']] = player['role_desc']
        
    group2idx = {}
    players = config['scenes'][1]['players']
    for i, player in enumerate(players):
        if isinstance(player, str):
            group2idx[player] = i
    
    customers = players_name
    
    exps_name = os.listdir(path) 
    exps = [exp for exp in exps_name if 'single' in exp ]    

    log = open('log_single.txt', 'a')
    customers_reason = {}
    for customer in customers:
        log.write(f'Customer: {customer}\n')
        role_desc = player2role[customer]
        customer_reason = {}
        
        for exp in exps:
            log.write(f'Experiment: {exp}\n')
            
            exp_path = os.path.join(path, exp)
            index = player2idx[customer] if 'single' in exp else group2idx[customer]
            file_name = f'purchase_{index}'
            content = open(os.path.join(exp_path, file_name), 'r')
            content = content.read()            

            def regular_match(content):
                pattern = r"\"reason\"(.*?)}"
                res = re.findall(pattern, content, re.S)
                format_tag = "Only compare"
                res = [r.strip() for r in res if format_tag not in r]
                return res

            def regular_match_2(content):
                pattern = r"\"summary\"(.*?)}"
                res = re.findall(pattern, content, re.S)
                # res = re.findall(pattern, content)
                format_tag = "including why this"
                res = [r.strip() for r in res if format_tag not in r]
                return res            
            
            processes = regular_match(content)

            cnt = {}
            for process in processes:
                
                prompt = prompt_template.format(process=process, role_desc=role_desc)
                ans = get_gpt_response(prompt)
                print(ans)
                pattern = r"[1-6]"
                ans = re.findall(pattern, ans)
                print(ans)
                
                ans_str = ','.join(ans)
                log.write(f'Reason: {ans_str}\n')
                for r in ans:
                    if r not in customer_reason:
                        customer_reason[r] = 1
                    else:
                        customer_reason[r] += 1
  
                    if r not in cnt:
                        cnt[r] = 1
                    else:
                        cnt[r] += 1
            log.write(f'one exp reason dict: {cnt}\n')
        log.write(f'{customer}: {customer_reason}\n')
        customers_reason[customer] = customer_reason
        print(customers_reason)
    print(customers_reason)        
       
if __name__ == "__main__":

    single_reason('./logs')
    
    # 创建两个进程，分别运行func1和func2，并传递参数
    # process1 = multiprocessing.Process(target=single_reason)
    # process2 = multiprocessing.Process(target=group_reason)

    # # 启动进程
    # process1.start()
    # process2.start()

    # # 等待两个进程完成
    # process1.join()
    # process2.join()

    # print("Both functions have finished.")