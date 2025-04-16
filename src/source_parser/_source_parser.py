from typing import Self
import pandas as pd

from abc import ABC, abstractmethod


class SourceParser(ABC):
    """
    Base class for source parsers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of the parser.
        """
        pass

    @abstractmethod
    def parse(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Parse the source and return a dictionary of data.
        """
        pass

    @classmethod
    def parser_from_name(cls, name: str) -> Self:
        for parser in cls.__subclasses__():
            if parser.name == name:
                return parser

        raise ValueError(f"Parser {name} not found.")
