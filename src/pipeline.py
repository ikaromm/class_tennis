from src.config.pipeline_config import PipelineConfig
from src.loader import BaseDataLoader
from src.source_parser._base_parser import BaseDataParser
from src.config.dataset_type import DatasetType


from src.transformers.transformers import (
    invert_winner_loser_names,
    inverter_scores_df,
    compute_rating_features,
    extract_score_features,
    prepare_tennis_model_data,
    finalize_tennis_model_data,
    create_dummy_variables,
    scale_numerical_features,
)


class PipelineRunner:
    @staticmethod
    def run(config: PipelineConfig):
        loader = BaseDataLoader.from_config(config)

        data = loader.process()

        parser = BaseDataParser.from_config(data, config)

        data = parser.process()

        if config.get("dataset_type") == DatasetType.TENNIS_MATCH:
            data = invert_winner_loser_names(data)
            data = inverter_scores_df(data)

            df_features = compute_rating_features(data)

            score_feats = data.apply(
                extract_score_features, axis=1, result_type="expand"
            )

            df_model_feats = prepare_tennis_model_data(data, score_feats)

            df_model_feats = finalize_tennis_model_data(
                data, df_model_feats, df_features
            )

            df_dummies = create_dummy_variables(
                df=df_model_feats,
                standard_dummy_cols=["best_of", "surface", "round"],
                reduced_category_config=[
                    ("tourney_level", 3),
                    ("player_A_hand", 1),
                    ("player_B_hand", 1),
                ],
                cols_to_drop=[
                    "tourney_name",
                    "tourney_level",
                    "player_A_hand",
                    "player_B_hand",
                ],
            )
            columns_to_scale = [
                "player_B_ht",
                "player_B_age",
                "player_A_ht",
                "player_A_age",
            ]
            df_scaled = scale_numerical_features(df_dummies, columns_to_scale)

        loader.save_data(df_scaled, config.get("path"))
