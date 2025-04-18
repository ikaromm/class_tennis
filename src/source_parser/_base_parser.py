from src.config.dataset_type import DatasetType
from src.config.pipeline_config import PipelineConfig

import pandas as pd

from abc import ABC, abstractmethod
from typing import Any, Unpack






class BaseDataParser(ABC):
    """
    Abstract base class for data parsing operations.
    Defines the interface for all data parsers in the system.
    """
    dataset_type: DatasetType = None

    def __init__(self, **config: Unpack[PipelineConfig]):
        """
        Initialize the data parser with optional configuration.

        Args:
            config: Configuration dictionary with parser-specific settings
        """
        self.config = config

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self.parse(data)

        if not self._validate_parsed_data(data):
            raise RuntimeError("Dado Invalido")
        
        return data

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

    def _validate_parsed_data(self, data: pd.DataFrame) -> bool:
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

    @classmethod
    def from_config(cls, config: PipelineConfig):
        for sub_clz in cls.__subclasses__():
            if sub_clz.dataset_type != config["dataset_type"]:
                continue

            return sub_clz(**config)

        raise NotImplemented