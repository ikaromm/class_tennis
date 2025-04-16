from pathlib import Path

from cache.cache_interface import CacheInterface
from class_tennis.src.data_validator import DataValidatorPipeline
from source_parser import SourceParser
from generate_data import generate_test_data

import re
import pandas as pd
import os


def generate_initial_data(arquivo: Path, fornecedor: str) -> dict:
    data = pd.DataFrame()
    for f in os.listdir(arquivo):
        data_place_holder = pd.read_csv(
            f"/Users/ikaromoribayashi/Documents/projects/class_tennis/data/{fornecedor}/{f}"
        )
        data = pd.concat([data, data_place_holder], ignore_index=True)

    # data = pd.read_parquet(arquivo, engine="pyarrow")

    imp = SourceParser.parser_from_name(fornecedor)

    data = imp().parse(data)

    return DataValidatorPipeline.validate(data)


def main(fornecedor: str, arquivo: Path):

    cache = CacheInterface(arquivo.with_suffix(".cache.p1"))

    data = None
    if not cache.check_exists():
        data = generate_initial_data(arquivo, fornecedor)

        cache.save(data)
    else:
        data = cache.load()

    print(data)
    if data is None:
        raise ValueError("No data found.")


if __name__ == "__main__":

    tasks = [
        (
            "tennis",
            Path(
                "/Users/ikaromoribayashi/Documents/projects/class_tennis/data/tennis/"
            ),
        ),
    ]

    for fornecedor, arquivo in tasks:
        # generate_test_data(arquivo)
        main(fornecedor=fornecedor, arquivo=arquivo)
