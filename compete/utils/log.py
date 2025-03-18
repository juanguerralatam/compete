import pandas as pd
import logging

def log_table(log_path, data, column_name):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    csv_file = f'{log_path}.csv'
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        df = pd.DataFrame()
    if 'name' not in df.columns:
        df['name'] = data.keys()
        df[column_name] = data.values()
    else:
        try:
            ordered_values = [data[name] for name in df['name']]
            df[column_name] = ordered_values
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            logging.debug(f"Data: {data}")
            logging.debug(f"Data keys: {data.keys()}")
            logging.debug(f"Data values: {data.values()}")
            raise
    logging.info(f"Data logged to {csv_file}")
    df.to_csv(csv_file, index=False)