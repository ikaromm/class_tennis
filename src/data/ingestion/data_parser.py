from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional, Union


class BaseDataParser(ABC):
    """
    Abstract base class for data parsing operations.
    Defines the interface for all data parsers in the system.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data parser with optional configuration.

        Args:
            config: Configuration dictionary with parser-specific settings
        """
        self.config = config or {}

    def validate_parsed_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the parsed data.

        Args:
            data: DataFrame to validate

        Returns:
            True if data is valid, False otherwise
        """
        # Basic validation: check if data is not empty
        if data.empty:
            return False

        # Check required columns if specified in config
        if "required_columns" in self.config:
            for col in self.config["required_columns"]:
                if col not in data.columns:
                    return False

        return True

    @abstractmethod
    def _standardize_column_names(data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to a consistent format.

        Args:
            data: DataFrame with original column names

        Returns:
            DataFrame with standardized column names
        """
        pass

    @abstractmethod
    def _process_player_information(data: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize player information.

        Args:
            data: DataFrame with player information

        Returns:
            DataFrame with processed player information
        """
        pass

    @abstractmethod
    def _process_match_statistics(data: pd.DataFrame) -> pd.DataFrame:
        """
        Process and standardize match statistics.

        Args:
            data: DataFrame with match statistics

        Returns:
            DataFrame with processed match statistics
        """

        pass

    @abstractmethod
    def _process_date_column(data: pd.DataFrame, columns: List[str]):
        """
        Select specific columns from the input data.

        Args:
            data: Input data to select columns from
            columns: List of column names to select

        Returns:
            DataFrame with selected columns
        """
        pass

    @abstractmethod
    def parse(data: Any) -> pd.DataFrame:
        """
        Parse the input data into a structured DataFrame.

        Args:
            data: Input data to parse

        Returns:
            Parsed DataFrame
        """
        pass


class TennisMatchParser(BaseDataParser):
    """
    Parser for tennis match data.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        data_col: List[str],
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(config)
        self.data = data
        self.data_col = data_col

    def parse(self) -> pd.DataFrame:
        """
        Parse tennis match data into a standardized format.

        Args:
            data: Input tennis match data

        Returns:
            Parsed and standardized DataFrame
        """
        # Make a copy to avoid modifying the original data
        parsed_data = self.data.copy()

        # Standardize column names
        parsed_data = self._standardize_column_names(parsed_data)
        print(self.data_col)
        # Extract and transform date information
        if len(self.data_col) > 0:
            parsed_data = self._process_date_column(parsed_data, self.data_col)

        # Process player information
        parsed_data = self._process_player_information(parsed_data)

        # Process match statistics
        parsed_data = self._process_match_statistics(parsed_data)

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

        # Convert all column names to lowercase and replace spaces with underscores
        data.columns = [col.lower().replace(" ", "_") for col in data.columns]

        return data

    def _process_date_column(
        self, data: pd.DataFrame, data_col: List[str]
    ) -> pd.DataFrame:
        """
        Process and standardize date information.

        Args:
            data: DataFrame with date column

        Returns:
            DataFrame with processed date information
        """
        try:
            for col in data_col:

                data[col] = pd.to_datetime(data[col])

                # Format date as YYYY-MM-DD (year-month-day only)
                data[col] = data[col].dt.strftime("%Y-%m-%d")

                # Extract additional date components
                data["year"] = pd.to_datetime(data[col]).dt.year
                data["month"] = pd.to_datetime(data[col]).dt.month
                data["day"] = pd.to_datetime(data[col]).dt.day

                # Create a concatenated column with year, month, and day
                data["date_concat"] = (
                    data["year"].astype(str)
                    + "-"
                    + data["month"].astype(str).str.zfill(2)
                    + "-"
                    + data["day"].astype(str).str.zfill(2)
                )

        except Exception as e:
            print(f"Warning: Failed to process date column: {str(e)}")

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
