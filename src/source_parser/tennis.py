from source_parser._source_parser import SourceParser


import pandas as pd


class TennisParser(SourceParser):
    name = "tennis"

    def parse(self, data: pd.DataFrame) -> pd.DataFrame:

        return data


SourceParser.parser_from_name("tennis")
