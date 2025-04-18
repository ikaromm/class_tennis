from tempfile import TemporaryDirectory, tempdir
from unittest import TestCase
from unittest import mock
from unittest.mock import mock_open

from src.config.pipeline_config import PipelineConfig
from src.loader.csv_data_loader import CSVDataLoader
from tests import test_config


class TestDataLoader(TestCase):
    def setUp(self):
        self.test_dataset_path = "dataset/"

    def test_cannot_instantiate(self):
        test_config = PipelineConfig()

        with self.assertRaises(RuntimeError):
            CSVDataLoader("invalid_file", **test_config)

    def test_process(self):
        test_config = PipelineConfig()

        loader = CSVDataLoader(self.test_dataset_path, **test_config)

        test_df = loader.process()

        self.assertTrue(len(test_df) > 0)

    def test_load_data(self):
        test_config = PipelineConfig()

        loader = CSVDataLoader(self.test_dataset_path, **test_config)

        test_df = loader.load_data()

        self.assertTrue(len(test_df) > 0)

    def test_validate(self):
        test_config = PipelineConfig()

        loader = CSVDataLoader(self.test_dataset_path, **test_config)

        test_df = loader.load_data()

        self.assertTrue(
            loader.validate_data(test_df)
        )

    def test_validate_dataset_empty(self):
        test_config = PipelineConfig()

        with TemporaryDirectory() as tmp_dir:
            loader = CSVDataLoader(tmp_dir, **test_config)

            test_df = loader.load_data()

            self.assertFalse(
                loader.validate_data(test_df)
            )

    def test_validate_dataset_required_column_not_found(self):
        test_config = PipelineConfig(
            required_columns=["banana"]
        )

        loader = CSVDataLoader(self.test_dataset_path, **test_config)

        test_df = loader.load_data()

        self.assertFalse(
            loader.validate_data(test_df)
        )