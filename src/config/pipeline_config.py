from typing import Literal, NotRequired, TypedDict

from src.config.load_type import LoaderType


class FileLoadConfig(TypedDict):
    delimiter: str
    encoding: str
    header: list[str]


class PipelineConfig(TypedDict):
    loader_type: LoaderType

    dataset_type: 
    dataset_path: str

    file_config: NotRequired[FileLoadConfig]
    required_columns: NotRequired[list[str]]
