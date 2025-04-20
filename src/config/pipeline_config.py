from typing import Literal, NotRequired, TypedDict

from src.config.load_type import LoaderType
from src.config.dataset_type import DatasetType


class FileLoadConfig(TypedDict):
    delimiter: str
    encoding: str
    header: list[str]


class PipelineConfig(TypedDict):
    dataset_type: DatasetType
    loader_type: LoaderType
    dataset_path: str

    file_config: NotRequired[FileLoadConfig]
    required_columns: NotRequired[list[str]]
