# Tennis Match Prediction Pipeline

A modular, object-oriented machine learning pipeline for predicting tennis match outcomes.

## Project Overview

This project implements a comprehensive machine learning system for tennis match prediction. The system uses historical match data to train models that can predict the outcome of future matches based on player statistics, surface information, and other relevant factors.

## Key Features

- Modular architecture with clear separation of concerns
- Flexible data loading from multiple sources
- Comprehensive data transformation pipeline
- Efficient caching mechanisms
- Configuration-driven component instantiation
- Comprehensive testing suite

## Project Structure

```
src/
├── loader/                # Data loading modules
│   ├── _base_data_loader.py
│   └── csv_data_loader.py
├── source_parser/         # Parsing modules for different data sources
│   ├── _base_parser.py
│   └── tennis_match_parser.py
├── transformers/          # Data transformation modules
│   └── log_data.py
├── cache/                 # Caching mechanisms
│   └── cache_interface.py
├── config/                # Configuration modules
│   ├── dataset_type.py
│   ├── load_type.py
│   └── pipeline_config.py
└── pipeline.py            # Main pipeline orchestration
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/class_tennis.git
cd class_tennis

# Install dependencies using Poetry
poetry install
```

## Usage

The pipeline is designed to be used as follows:

```python
from src.pipeline import PipelineRunner
from src.config.pipeline_config import PipelineConfig

# Create a configuration
config = PipelineConfig({
    "load_type": "CSV",
    "dataset_type": "TENNIS_MATCH",
    "path": "path/to/your/data.csv"
})

# Run the pipeline
PipelineRunner.run(config)
```

## Data Processing Flow

1. **Data Loading**: The pipeline loads data from the specified source using the appropriate loader
2. **Data Parsing**: The loaded data is parsed according to the dataset type
3. **Data Transformation**: Transformers are applied to the parsed data
4. **Data Storage**: The processed data is saved to the specified location

## Extending the Pipeline

### Adding a New Data Loader

1. Create a new class that inherits from `BaseDataLoader`
2. Implement the required methods (`process`, `save_data`)
3. Register the loader in the `BaseDataLoader.from_config` method

### Adding a New Parser

1. Create a new class that inherits from `BaseDataParser`
2. Implement the required methods (`process`)
3. Register the parser in the `BaseDataParser.from_config` method

### Adding a New Transformer

1. Create a new function that takes a DataFrame and returns a transformed DataFrame
2. Add the transformer to the `PipelineRunner.transformer` list

## Testing

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src
```

## Documentation

For more detailed information about the project architecture and design decisions:

- [Project Design Requirements (PDR)](PDR.md)
- [Architecture Decision Record (ADR)](ADR.md)

## License

[MIT](LICENSE)
