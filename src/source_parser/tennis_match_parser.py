from src.config.dataset_type import DatasetType
from src.config.pipeline_config import PipelineConfig
from src.source_parser._base_parser import BaseDataParser

import pandas as pd
from typing import Dict, Any, List, Optional, Unpack


class TennisMatchParser(BaseDataParser):
    """
    Parser for tennis match data.
    """

    dataset_type = DatasetType.TENNIS_MATCH

    def __init__(
        self,
        data: pd.DataFrame,
        **config: Unpack[PipelineConfig],
    ):
        super().__init__(**config)
        self._data_col = "tourney_date"
        self.data = data

    def parse(self) -> pd.DataFrame:
        """
        Parse tennis match data into a standardized format.

        Args:
            data: Input tennis match data

        Returns:
            Parsed and standardized DataFrame
        """

        if not super()._validate_parsed_data(self.data):
            raise ValueError("Dado Invalido")

        self.data["outcome"] = 1

        parsed_data = self.data.copy()

        parsed_data = self._standardize_column_names(parsed_data)

        parsed_data = self._process_date_column(parsed_data)

        parsed_data = self._process_player_information(parsed_data)

        parsed_data = self._process_match_statistics(parsed_data)

        parsed_data["match_id"] = parsed_data.index

        return parsed_data

    def _standardize_column_names(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to a consistent format.

        Args:
            data: DataFrame with original column names

        Returns:
            DataFrame with standardized column names
        """
        # Column name mapping from config or default mapping
        column_mapping = self.config.get("column_mapping", {})

        # Apply mapping if provided
        if column_mapping:
            data = data.rename(columns=column_mapping)

        return data

    def _process_date_column(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize date information.

        Args:
            data: DataFrame with date column

        Returns:
            DataFrame with processed date information
        """
        data["tourney_date"] = pd.to_datetime(data["tourney_date"], format="%Y%m%d")

        data["tourney_datetime"] = data["tourney_date"] + pd.to_timedelta(
            data.groupby(["tourney_date"]).cumcount(), unit="s"
        )

        data = data.sort_values(by="tourney_datetime").reset_index(drop=True)

        data = data.drop(columns=["tourney_date"])

        return data

    def _process_player_information(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize player information.

        Args:
            data: DataFrame with player information

        Returns:
            DataFrame with processed player information
        """

        return data

    def _process_match_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize match statistics.

        Args:
            data: DataFrame with match statistics

        Returns:
            DataFrame with processed match statistics
        """

        return data
