from pathlib import Path
import pandas as pd
import os
from typing import Dict, Any, Unpack

from src.config.load_type import LoaderType
from src.config.pipeline_config import PipelineConfig
from src.loader._base_data_loader import BaseDataLoader


class CSVDataLoader(BaseDataLoader):
    """
    Data loader for CSV files.
    """
    loader_type = LoaderType.CSV

    def __init__(self, dataset_path: str|Path, **config: Unpack[PipelineConfig]):
        """
        Initialize the CSV data loader.

        Args:
            dataset_path: Path to the CSV file
            config: Configuration dictionary with loader-specific settings
        """
        super().__init__(**config)
        
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise RuntimeError("Dataset path not found")
        
        self.dataset_path = Path(dataset_path)

    def load_data(self) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Returns:
            DataFrame containing the loaded data
        """
        try:
            data = pd.DataFrame()

            for file in self.dataset_path.rglob("*.csv"):
                data_holder = pd.read_csv(
                    file, **self._get_csv_options()
                )
                data = pd.concat([data, data_holder], ignore_index=True)

            return data
        except Exception as e:
            raise RuntimeError(f"Failed to load data from {self.dataset_path}: {str(e)}")

    def save_data(self, data: pd.DataFrame, path: str) -> None:
        """
        Save data to a file.

        Args:
            data: DataFrame to save
            path: Path where to save the data
        """
        data.to_csv(path, index=False)

    def _get_csv_options(self) -> Dict[str, Any]:
        """
        Get pandas read_csv options from config.

        Returns:
            Dictionary with read_csv options
        """
        return self.config.get("file_config", {})

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
        if (
            "required_columns" in self.config and 
            not all(col in data.columns for col in self.config["required_columns"])
        ):
            return False

        return True
