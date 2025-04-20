from unittest import TestCase

from src.config.dataset_type import DatasetType
from src.config.load_type import LoaderType
from src.config.pipeline_config import PipelineConfig
from src.pipeline import PipelineRunner


class TestPipeline(TestCase):
    def test_pipeline(self):
        config = PipelineConfig(
            dataset_type=DatasetType.TENNIS_MATCH,
            dataset_path="dataset/",
            loader_type=LoaderType.CSV,
            path="dataset/test",
            data_col="tourney_date",
        )

        PipelineRunner.run(config)
