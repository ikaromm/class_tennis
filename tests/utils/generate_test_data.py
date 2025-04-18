import pandas as pd


def generate_test_data() -> pd.DataFrame:
    test_file_path = "src/data/archives/tennis/atp_matches_1985.csv"
    return pd.read_csv(test_file_path, sep=",")
