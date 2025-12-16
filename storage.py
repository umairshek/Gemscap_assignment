import pandas as pd
import os

def save_tick(symbol, tick):
    if not os.path.exists("data"):
        os.mkdir("data")

    file_path = f"data/{symbol}.csv"
    df = pd.DataFrame([tick])
    df.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)

def load_data(symbol):
    file_path = f"data/{symbol}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()
