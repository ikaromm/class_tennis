from src.loader.csv_data_loader import CSVDataLoader
from src.source_parser.tennis_match_parser import TennisMatchParser


def main():

    config = {"required_columns": ["tourney_id", "tourney_name", "surface"]}

    data_loader = CSVDataLoader(
        "dataset",
        config=config,
    )

    data = data_loader.load_data()

    if data_loader.validate_data(data):

        print(data.shape)
        data_col = ["tourney_date"]

        tennis_match_parser = TennisMatchParser(data)
        data = tennis_match_parser.parse()

        if data_loader.validate_data(data):
            print(data.head())
            print(data.shape)
    else:
        raise ValueError("Data is not valid")


if __name__ == "__main__":
    main()
