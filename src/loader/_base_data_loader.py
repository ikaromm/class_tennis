from abc import ABC, abstractmethod
import pandas as pd
import os
from typing import Unpack

from src.config.load_type import LoaderType
from src.config.pipeline_config import PipelineConfig


class BaseDataLoader(ABC):
    loader_type: LoaderType = None

    """
    Abstract base class for data loading operations.
    Defines the interface for all data loaders in the system.
    """

    def __init__(self, **config: Unpack[PipelineConfig]):
        """
        Initialize the data loader with optional configuration.

        Args:
            config: Configuration dictionary with loader-specific settings
        """
        self.config = config

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """
        Load data from the source.

        Returns:
            DataFrame containing the loaded data
        """
        raise NotImplementedError

    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate the loaded data.

        Args:
            data: DataFrame to validate

        Returns:
            True if data is valid, False otherwise
        """
        return True

    @abstractmethod
    def save_data(self, data: pd.DataFrame, path: str) -> None:
        """
        Save data to a file.

        Args:
            data: DataFrame to save
            path: Path where to save the data
        """
        pass

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

    @classmethod
    def from_config(cls, config: PipelineConfig):
        for sub_clz in cls.__subclasses__():
            if sub_clz.loader_type != config["loader_type"]:
                continue
            return sub_clz(**config)

        raise NotImplementedError
