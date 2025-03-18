# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import re
import csv
import json
import yaml
import numpy as np
import requests
from .draw import Draw
from .prompt import PromptTemplate


openai_api_key = os.getenv("OPENAI_KEY")


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
    return response

def read_csv(path, fields):
    res = {}
    
    if isinstance(fields, str):
        fields = [fields]
        
    with open(path, mode='r') as file:
        csv_reader = csv.reader(file)    
        for row in csv_reader:
            if row[0] in fields:
                res[row[0]] = row[1:]

    return res

# wirte data into csv file
def write_csv(path, data):
    # data is a dict
    with open(path, mode='a') as file:
        csv_writer = csv.writer(file)
        for key, value in data.items():
            csv_writer.writerow([key] + value)

def analysis_portfolio(portfolio1, portfolio2):
    if isinstance(portfolio1, str):
        portfolio1 = json.loads(portfolio1)
    if isinstance(portfolio2, str):
        portfolio2 = json.loads(portfolio2)
    
    # 计算两个公司的各自产品的数量
    num_product1 = len(portfolio1)
    num_product2 = len(portfolio2)

    # 计算每个公司的产品的平均价格
    price1 = [product['price'] for product in portfolio1]
    avg_price1 = sum(price1) / len(price1)

    price2 = [product['price'] for product in portfolio2]
    avg_price2 = sum(price2) / len(price2)
    
    # 向gpt查询两个产品组合中相同的产品，记录相似产品的数量
    prompt_template = PromptTemplate(["analysis_portfolio"])
    prompt = prompt_template.render(data=[portfolio1, portfolio2])
    print(prompt)
    response = get_gpt_response(prompt)
    print(response)
    
    # find first { and last }
    pattern = r"\{[\s\S]*\}"

    response = re.findall(pattern, response)[0]
    print(response)
    response = json.loads(response)

    similar_product1 = response['company1']
    similar_product2 = response['company2']

    num_similar_product = len(similar_product1)

    # 计算两个公司的相似产品的平均价格, 遍历产品组合查看每个产品的id是否在similar_product中
    similar_price1 = []
    similar_price2 = []

    for product in portfolio1:
        if product['id'] in similar_product1:
            similar_price1.append(product['price'])

    for product in portfolio2:
        if product['id'] in similar_product2:
            similar_price2.append(product['price'])
        
    avg_similar_price1 = sum(similar_price1) / num_similar_product
    avg_similar_price2 = sum(similar_price2) / num_similar_product
    
    # put data into a dict
    data = {
        'num_product1': num_product1,
        'num_product2': num_product2,
        'num_similar_product': num_similar_product,
        'avg_price1': avg_price1,
        'avg_price2': avg_price2,
        'avg_similar_price1': avg_similar_price1,
        'avg_similar_price2': avg_similar_price2
    }
    
    return data

def analysis_portfolio2(portfolio1, portfolio2):
    if isinstance(portfolio1, str):
        portfolio1 = json.loads(portfolio1)
    if isinstance(portfolio2, str):
        portfolio2 = json.loads(portfolio2)
        
    # 计算产品的平均性价比
    price1 = [product['price'] for product in portfolio1]
    cost_price1 = [product['cost_price'] for product in portfolio1]
    # 计算每一个产品的性价比最后取平均
    avg_score1 = sum([c / p for p, c in zip(price1, cost_price1)]) / len(price1)
    
    price2 = [product['price'] for product in portfolio2]
    cost_price2 = [product['cost_price'] for product in portfolio2]
    avg_score2 = sum([c / p for p, c in zip(price2, cost_price2)]) / len(price2)
    
    return {
        'avg_score1': avg_score1,
        'avg_score2': avg_score2
    }

def analysis_portfolios(path1, path2):
    res = []
    
    # from two path read the portfolios in csv file
    portfolios1 = read_csv(path1, fields=['portfolio'])['portfolio']
    portfolios2 = read_csv(path2, fields=['portfolio'])['portfolio']
    
    # call analysis_portfolio to analyze the portfolios
    for portfolio1, portfolio2 in zip(portfolios1, portfolios2):
        data = analysis_portfolio(portfolio1, portfolio2)
        res.append(data)
    
    # analysis the res and draw the graph
    avg_price1 = []
    avg_price2 = []
    avg_similar_price1 = []
    avg_similar_price2 = []
    similar_proportion = []
    for r in res:
        avg_price1.append(r['avg_price1'])
        avg_price2.append(r['avg_price2'])
        avg_similar_price1.append(r['avg_similar_price1'])
        avg_similar_price2.append(r['avg_similar_price2'])
        
        p = 2 * r['num_similar_product'] / (r['num_product1'] + r['num_product2'])
        similar_proportion.append(p)
    
    # get the parent path
    path = os.path.dirname(path1)
    path = os.path.dirname(path)
    # write data into csv file
    # write_csv(os.path.join(path, 'portfolio.csv'), {
    #     'avg_price1': avg_price1,
    #     'avg_price2': avg_price2,
    #     'avg_similar_price1': avg_similar_price1,
    #     'avg_similar_price2': avg_similar_price2,
    #     'similar_proportion': similar_proportion
    # })
    
    return {
        'avg_price1': avg_price1,
        'avg_price2': avg_price2,
        'avg_similar_price1': avg_similar_price1,
        'avg_similar_price2': avg_similar_price2,
        'similar_proportion': similar_proportion
    }  

# 计算性价比 
def analysis_portfolios2(path1, path2):
    res = []
    
    # from two path read the portfolios in csv file
    portfolios1 = read_csv(path1, fields=['portfolio'])['portfolio']
    portfolios2 = read_csv(path2, fields=['portfolio'])['portfolio']
    
    # call analysis_portfolio2 to analyze the portfolios
    for portfolio1, portfolio2 in zip(portfolios1, portfolios2):
        data = analysis_portfolio2(portfolio1, portfolio2)
        res.append(data)
    
    # analysis the res and draw the graph
    avg_score1 = []
    avg_score2 = []
    for r in res:
        avg_score1.append(r['avg_score1'])
        avg_score2.append(r['avg_score2'])
    
    # get the parent path
    path = os.path.dirname(path1)
    path = os.path.dirname(path)
    # write data into csv file
    write_csv(os.path.join(path, 'portfolio.csv'), {
        'avg_score1': avg_score1,
        'avg_score2': avg_score2
    })
    
    # return {
    #     'avg_score1': avg_score1,
    #     'avg_score2': avg_score2
    # }

def analysis_data(path1, path2):
    # from two path read the data in csv file
    data1 = read_csv(path1, fields=['num_of_customer', 'product_score', 'customer_score'])
    data2 = read_csv(path2, fields=['num_of_customer', 'product_score', 'customer_score'])
    
    num_of_customer1 = [int(d) for d in data1['num_of_customer']]
    num_of_customer2 = [int(d) for d in data2['num_of_customer']]
    
    product_score1 = [float(d) for d in data1['product_score']]
    product_score2 = [float(d) for d in data2['product_score']]
    
    customer_score1 = [float(d) for d in data1['customer_score']]
    customer_score2 = [float(d) for d in data2['customer_score']]
    
    return {
        'num_of_customer1': num_of_customer1,
        'num_of_customer2': num_of_customer2,
        'product_score1': product_score1,
        'product_score2': product_score2,
        'customer_score1': customer_score1,
        'customer_score2': customer_score2
    }

def analysis_basic_data(path):
    draw = Draw(path)
    
    # Part1: analysis the portfolios
    portfolio_path1 = os.path.join(path, 'strategy_9000', 'portfolio.csv')
    portfolio_path2 = os.path.join(path, 'strategy_9001', 'portfolio.csv')
    
    data = analysis_portfolios(portfolio_path1, portfolio_path2)
    
    draw.similar_proportion(data['similar_proportion'])
    draw.avg_score(data['avg_score1'], data['avg_score2'])
    draw.similar_avg_score(data['avg_similar_score1'], data['avg_similar_score2'])
    
    # Part2: analysis the scores
    data_path1 = os.path.join(path, 'strategy_9000', 'data.csv')
    data_path2 = os.path.join(path, 'strategy_9001', 'data.csv')
    
    data = analysis_data(data_path1, data_path2)
    
    draw.customer_flow(data['num_of_customer1'], data['num_of_customer2'])
    draw.product_score(data['product_score1'], data['product_score2'])
    draw.customer_score(data['customer_score1'], data['customer_score2'])
    
def analysis_customer_flow_with_annotation(path):
    data_path1 = os.path.join(path, 'strategy_9000', 'data.csv')    
    data_path2 = os.path.join(path, 'strategy_9001', 'data.csv')
    
    data1 = read_csv(data_path1, fields=['num_of_customer'])
    data2 = read_csv(data_path2, fields=['num_of_customer'])
    
    num_of_customer1 = [int(d) for d in data1['num_of_customer']]
    num_of_customer2 = [int(d) for d in data2['num_of_customer']]
    
    draw = Draw(path)
    
    draw.customer_flow_with_annotation(num_of_customer1, num_of_customer2)

def analysis_customer_flow_with_score(path):
    data_path1 = os.path.join(path, 'strategy_9000', 'data.csv')    
    data_path2 = os.path.join(path, 'strategy_9001', 'data.csv')
    
    data1 = read_csv(data_path1, fields=['num_of_customer', 'customer_score'])
    data2 = read_csv(data_path2, fields=['num_of_customer', 'customer_score'])
    
    num_of_customer1 = [int(d) for d in data1['num_of_customer']]
    num_of_customer2 = [int(d) for d in data2['num_of_customer']]
    
    score1 = [float(d) for d in data1['customer_score']]
    score2 = [float(d) for d in data2['customer_score']]
    
    draw = Draw(path)

    draw.customer_flow_and_score(num_of_customer1, num_of_customer2, score1, score2)

def analysis_customer_reason(path):
        
    data_list = [
        [213, 45, 198, 22, 67, 2],
        [225, 19, 162, 0, 84, 24],
        [225, 18, 138, 14, 60, 32],
        [224, 18, 146, 1, 138, 55],
        [167, 43, 180, 2, 176, 63],
        [225, 1, 139, 11, 64, 30],
        [225, 31, 120, 119, 13, 19],
        [225, 17, 180, 1, 154, 21],
        [115, 22, 181, 7, 137, 103],
        [158, 45, 170, 13, 129, 51],
        [91, 57, 40, 1, 82, 38],
        [87, 45, 35, 11, 87, 52],
        [91, 65, 28, 45, 56, 36],
        [84, 51, 34, 55, 64, 43],
        [76, 53, 39, 2, 84, 80],
        [91, 54, 28, 55, 55, 23],
        [90, 48, 28, 6, 83, 67],
        [88, 50, 32, 2, 81, 65],
        [91, 64, 38, 3, 75, 43],
        [87, 50, 33, 7, 82, 48],
        [92, 58, 46, 56, 61, 42],
        [90, 65, 34, 2, 75, 50],
        [91, 47, 32, 30, 66, 50],
        [91, 58, 43, 30, 74, 46],
        [91, 51, 29, 62, 57, 40]
    ]
    
    #     Oscar
    # Umar
    # Katie
    # Zach
    # Leo
    # David
    # Quincy
    # Jack
    # Xena
    # Bob
    # Family1
    # Family2
    # Family3
    # Family4
    # Colleague1
    # Colleague2
    # Colleague3
    # Colleague4
    # Couple1
    # Couple2
    # Couple3
    # Friend1
    # Friend2
    # Friend3
    # Friend4
    
    customer_name = ['Oscar', 'Umar', 'Katie', 'Zach', 'Leo', 'David', 'Quincy', 'Jack', 'Xena', 'Bob', 'Family1', 'Family2', 'Family3', 'Family4', 'Colleague1', 'Colleague2', 'Colleague3', 'Colleague4', 'Couple1', 'Couple2', 'Couple3', 'Friend1', 'Friend2', 'Friend3', 'Friend4']
    draw = Draw(path)
    draw.choice_percentage(data_list, customer_name)

def analysis(path, field='customer_flow'):
    if field == 'customer_flow_with_annotation':
        analysis_customer_flow_with_annotation(path)
    if field == 'customer_flow_with_score':
        analysis_customer_flow_with_score(path)
    if field == 'customer_reason':
        analysis_customer_reason(path)
    
def aggregate_data(path, field='product_score'):
    # get all folders in the logs folder
    exps_name = os.listdir(path)
    # get all exp named with 'single
    exps = [exp for exp in exps_name if 'single' in exp or 'group' in exp]

    list_1 = []
    list_2 = []
    for exp in exps:
        exp_path = os.path.join(path, exp)
        files_name = os.listdir(exp_path)
        if 'strategy_9000' in files_name:
            path1 = os.path.join(exp_path, 'strategy_9000', 'data.csv')
            path2 = os.path.join(exp_path, 'strategy_9001', 'data.csv')
        else:
            path1 = os.path.join(exp_path, 'strategy_9002', 'data.csv')
            path2 = os.path.join(exp_path, 'strategy_9003', 'data.csv')
        data1 = read_csv(path1, fields=[field])
        data2 = read_csv(path2, fields=[field])
        list_1.append(data1[field])
        list_2.append(data2[field])
    
    draw = Draw(path)
    draw.aggregate_two_line(list_1, list_2, field)
        
def aggregate_similar_prop(path):
    # get all folders in the logs folder
    exps_name = os.listdir(path)
    # get all exp named with 'single
    exps = [exp for exp in exps_name if 'single' in exp or 'group' in exp]
    
    list_1 = []
    list_2 = []
    for exp in exps:
        exp_path = os.path.join(path, exp)
        exp_path = os.path.join(exp_path, 'portfolio.csv')
        data = read_csv(exp_path, fields=['avg_price1', 'avg_price2', 'avg_similar_price1', 'avg_similar_price2', 'similar_proportion'])
        list_1.append(data['similar_proportion'])
    
    transposed_list = list(zip(*list_1))
    # calculate the standard deviation and mean
    stdev = []
    avg = []
    for item in transposed_list:
        item = np.array(item, dtype=float)
        stdev.append(np.std(item))
        avg.append(np.mean(item))
    
    draw = Draw(path)
    draw.similar_proportion(avg, stdev)

def aggreagte_similar_product_price(path):
    # get all folders in the logs folder
    exps_name = os.listdir(path)
    # get all exp named with 'single
    exps = [exp for exp in exps_name if 'single' in exp ]
    
    list_1 = []
    list_2 = []
    for exp in exps:
        exp_path = os.path.join(path, exp)
        exp_path = os.path.join(exp_path, 'portfolio.csv')
        data = read_csv(exp_path, fields=['avg_price1', 'avg_price2', 'avg_similar_price1', 'avg_similar_price2', 'similar_proportion'])
        list_1.append(data['avg_similar_price1'])
        list_2.append(data['avg_similar_price2'])
    
    draw = Draw(path)
    draw.aggregate_similar_avg_price(list_1, list_2)
       
def aggregate(path, field='product_score'):
    if field == 'similar_proportion':
        aggregate_similar_prop(path)
    elif field == 'avg_price':
        aggreagte_similar_product_price(path)
    else:
        aggregate_data(path, field=field)
