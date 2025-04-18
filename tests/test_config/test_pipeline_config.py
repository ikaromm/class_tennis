from src.config.pipeline_config import PipelineConfig

from unittest import TestCase



class TestPipelineConfig(TestCase):
    def test_create_config(self):
        config = PipelineConfig(
            required_columns=[]
        )
        
        self.assertEqual(
            config['required_columns'], []
        )