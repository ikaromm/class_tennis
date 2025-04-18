from ingestion.data_loader import CSVDataLoader
from ingestion.data_parser import TennisMatchParser


def main():

    config = {"required_columns": ["tourney_id", "tourney_name", "surface"]}

    data_loader = CSVDataLoader(
        "../data/archives/tennis/",
        config=config,
    )

    data = data_loader.load_data()

    if data_loader.validate_data(data):

        print(data.shape)
        data_col = ["tourney_date"]

        tennis_match_parser = TennisMatchParser(data, data_col=data_col)
        data = tennis_match_parser.parse()

        if data_loader.validate_data(data):
            print(data.head())
            print(data.shape)
    else:
        raise ValueError("Data is not valid")


if __name__ == "__main__":
    main()
