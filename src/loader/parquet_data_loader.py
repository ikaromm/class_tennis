from email.policy import default
import pandas as pd


class DataValidatorPipeline:
    @staticmethod
    def validate(data: pd.DataFrame) -> dict:
        """
        Validate the Data data.
        """

        data.to_parquet("data.parquet")
        return data
