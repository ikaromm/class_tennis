from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import Optional, Dict, Any, Union


class BaseDataLoader(ABC):
    """
    Abstract base class for data loading operations.
    Defines the interface for all data loaders in the system.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data loader with optional configuration.

        Args:
            config: Configuration dictionary with loader-specific settings
        """
        self.config = config or {}

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """
        Load data from the source.

        Returns:
            DataFrame containing the loaded data
        """
        pass

    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the loaded data.

        Args:
            data: DataFrame to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    def save_data(self, data: pd.DataFrame, path: str) -> None:
        """
        Save data to a file.

        Args:
            data: DataFrame to save
            path: Path where to save the data
        """
        data.to_csv(path, index=False)

    def process(self) -> pd.DataFrame:
        """
        Process the data loading pipeline.

        Returns:
            Processed DataFrame
        """
        data = self.load_data()
        if not self.validate_data(data):
            raise ValueError("Data validation failed")
        return data


class CSVDataLoader(BaseDataLoader):
    """
    Data loader for CSV files.
    """

    def __init__(self, file_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CSV data loader.

        Args:
            file_path: Path to the CSV file
            config: Configuration dictionary with loader-specific settings
        """
        super().__init__(config)
        self.file_path = file_path

    def load_data(self) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Returns:
            DataFrame containing the loaded data
        """
        try:
            data = pd.DataFrame()
            for file in os.listdir(self.file_path):
                data_holder = pd.read_csv(
                    os.path.join(self.file_path, file), **self._get_csv_options()
                )
                data = pd.concat([data, data_holder], ignore_index=True)

            return data
        except Exception as e:
            raise IOError(f"Failed to load data from {self.file_path}: {str(e)}")

    def _get_csv_options(self) -> Dict[str, Any]:
        """
        Get pandas read_csv options from config.

        Returns:
            Dictionary with read_csv options
        """
        options = {}
        if "delimiter" in self.config:
            options["delimiter"] = self.config["delimiter"]
        if "encoding" in self.config:
            options["encoding"] = self.config["encoding"]
        if "header" in self.config:
            options["header"] = self.config["header"]
        return options

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the loaded data.

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
