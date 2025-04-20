from unittest import TestCase
from src.config.pipeline_config import PipelineConfig
from src.source_parser.tennis_match_parser import TennisMatchParser
from src.source_parser._base_parser import BaseDataParser
from src.loader.csv_data_loader import CSVDataLoader

import pandas as pd


class TestParser(TestCase):
    def setUp(self):
        self.test_dataset_path = "dataset/"

    def test_validate_parsed_data(self):
        test_config = PipelineConfig()

        test_df = pd.DataFrame()
        parser = TennisMatchParser(test_df, **test_config)

        with self.assertRaisesRegex(RuntimeError, r"^Dado Invalido$"):
            parser.process()

    def test_config_not_implemented(self):
        test_config = PipelineConfig()

        with self.assertRaises(NotImplementedError):
            TennisMatchParser(None, **test_config).from_config(None, test_config)
