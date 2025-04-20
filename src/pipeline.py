from typing import Callable
from src.config.pipeline_config import PipelineConfig
from src.loader import BaseDataLoader
from src.source_parser._base_parser import BaseDataParser

import pandas as pd

from src.transformers.log_data import log_data


class PipelineRunner:
    transformer: list[Callable[[pd.DataFrame], pd.DataFrame]] = [log_data]

    @staticmethod
    def run(config: PipelineConfig):
        loader = BaseDataLoader.from_config(config)

        data = loader.process()

        parser = BaseDataParser.from_config(data, config)

        data = parser.process()

        for trans in PipelineRunner.transformer:
            data = trans(data)

        loader.save_data(data, config.get("path"))
