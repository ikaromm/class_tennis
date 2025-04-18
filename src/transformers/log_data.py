import pandas as pd


def log_data(data: pd.DataFrame) -> pd.DataFrame:
    print(data.head())
    return data