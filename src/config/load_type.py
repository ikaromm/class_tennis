from enum import Enum


class LoaderType(Enum):
    CSV = "csv"
    PARQUET = "parquet"
    DB = "db"