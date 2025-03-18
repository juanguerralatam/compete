import pandas as pd

def log_table(log_path, data, column_name):
        csv_file = f'{log_path}.csv'
        try:
            df = pd.read_csv(csv_file)
        except FileNotFoundError:
            df = pd.DataFrame()

        if 'name' not in df.columns:
            df['name'] = data.keys()
            df[column_name] = data.values()
        else:
            ordered_values = [data[name] for name in df['name']]
            df[column_name] = ordered_values

        print(df)
        df.to_csv(csv_file, index=False)