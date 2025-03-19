import json
import requests
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_data_from_database(endpoint, port, base_url="http://localhost:", retries=3):
    url = f"{base_url}{port}/{endpoint}/"
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)  # Add timeout to prevent hanging
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                error_msg = f"Failed to get data from {url} with status code {response.status_code}"
                logging.error(f"Attempt {attempt + 1}: {error_msg}")
                logging.debug(f"Response content: {response.content}")
                last_error = error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request to {url} failed with error: {e}"
            logging.error(f"Attempt {attempt + 1}: {error_msg}")
            last_error = error_msg
        
        if attempt < retries - 1:  # Don't sleep on the last attempt
            time.sleep(1)  # Add delay between retries
    
    error_details = f"Error retrieving data for port {port}: {last_error}" if last_error else f"Failed to connect to database on port {port}"
    raise Exception(error_details)


def send_data_to_database(data, endpoint, port, base_url="http://localhost:"):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug(f"Data received: {data}")
    # handle the case when different types of res
    if isinstance(data, dict):
        res_list = [data]
    elif isinstance(data, list):
        res_list = data
    else:
        try:
            res_list = json.loads(data)
            if not isinstance(res_list, list):
                res_list = [res_list]
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            logging.debug(f"Data: {data}")
            raise Exception(f"error: data should be a dict or a list of dict \n {data}")
    
    url = f"{base_url}{port}/{endpoint}/"
    for res in res_list:
        data_type = res["type"]

        try:
            if data_type == "add":
                response = requests.post(url, json=res["data"])
            elif data_type == "delete":
                response = requests.delete(f"{url}{res['id']}/")
            elif data_type == "update":
                response = requests.put(f"{url}{res['id']}/", json=res["data"])
            elif data_type == "partial_update":
                response = requests.patch(f"{url}{res['id']}/", json=res["data"])
            elif data_type == "other":
                return
            else: 
                raise Exception(f"error: No this type - {data_type}")

            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
        
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTPError: {e}")
            raise Exception(f"type: {data_type}, endpoint: {endpoint}, port: {port}, data: {res}, error: {e}")
