import pandas as pd
import os
import math
from collections import defaultdict
from glicko2 import Player as Glicko2Player
import trueskill
import re
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def invert_winner_loser_names(data):
    indices_para_inverter = data.sample(frac=0.5).index

    colunas_pares = [
        ("winner_id", "loser_id"),
        ("winner_seed", "loser_seed"),
        ("winner_entry", "loser_entry"),
        ("winner_name", "loser_name"),
        ("winner_hand", "loser_hand"),
        ("winner_ht", "loser_ht"),
        ("winner_ioc", "loser_ioc"),
        ("winner_age", "loser_age"),
        ("winner_rank", "loser_rank"),
        ("winner_rank_points", "loser_rank_points"),
        ("w_ace", "l_ace"),
        ("w_df", "l_df"),
        ("w_svpt", "l_svpt"),
        ("w_1stIn", "l_1stIn"),
        ("w_1stWon", "l_1stWon"),
        ("w_2ndWon", "l_2ndWon"),
        ("w_SvGms", "l_SvGms"),
        ("w_bpSaved", "l_bpSaved"),
        ("w_bpFaced", "l_bpFaced"),
    ]

    for col_a, col_b in colunas_pares:
        temp = data.loc[indices_para_inverter, col_a].copy()
        data.loc[indices_para_inverter, col_a] = data.loc[indices_para_inverter, col_b]
        data.loc[indices_para_inverter, col_b] = temp

    data.loc[indices_para_inverter, "outcome"] = 0

    rename_dict = {}

    for col in data.columns:
        if col.startswith("winner_"):
            rename_dict[col] = col.replace("winner_", "player_A_")
        elif col.startswith("loser_"):
            rename_dict[col] = col.replace("loser_", "player_B_")
        elif col.startswith("w_"):
            rename_dict[col] = col.replace("w_", "player_A_")
        elif col.startswith("l_"):
            rename_dict[col] = col.replace("l_", "player_B_")

    data.rename(columns=rename_dict, inplace=True)

    return data


def inverter_score(score_str):
    if not isinstance(score_str, str):
        return score_str

    score_str = score_str.strip().upper()
    especiais = ["RET", "W/O", "WO", "RETIRE"]

    if any(score_str.startswith(e) for e in especiais):
        return score_str  # não inverte

    sets = score_str.split()
    sets_invertidos = []

    for s in sets:
        match = re.match(r"(\d+)-(\d+)(\(\d+\))?", s)
        if match:
            p1, p2, tb = match.groups()
            novo_set = f"{p2}-{p1}{tb or ''}"
            sets_invertidos.append(novo_set)
        else:
            sets_invertidos.append(s)

    return " ".join(sets_invertidos)


def inverter_scores_df(df, outcome_col="outcome", score_col="score", mutate=True):
    """
    Inverte as pontuações apenas onde outcome == 0.

    Parameters
    ----------
    df : pandas.DataFrame
        Tabela com colunas de outcome e score.
    outcome_col : str
        Nome da coluna que indica quem venceu (0 → inverter).
    score_col : str
        Nome da coluna com o placar em texto.
    mutate : bool
        Se True, altera o DataFrame original; senão, devolve uma cópia.
    """
    target = df if mutate else df.copy()
    mask = target[outcome_col] == 0
    target.loc[mask, score_col] = target.loc[mask, score_col].apply(inverter_score)
    return target


def compute_rating_features(df):
    elo = defaultdict(lambda: 1500)
    glicko = defaultdict(lambda: Glicko2Player())
    ts_env = trueskill.TrueSkill()
    ts_ratings = defaultdict(ts_env.Rating)

    rows = []

    for _, row in df.iterrows():
        A, B, result = row["player_A_name"], row["player_B_name"], row["outcome"]

        rA_e, rB_e = elo[A], elo[B]
        pA, pB = glicko[A], glicko[B]
        tA, tB = ts_ratings[A], ts_ratings[B]

        exp_e = 1 / (1 + 10 ** ((rB_e - rA_e) / 400))
        q = math.log(10) / 400
        g_phi = 1 / math.sqrt(1 + (3 * q**2 * pB.rd**2) / math.pi**2)
        exp_g = 1 / (1 + 10 ** (-g_phi * (pA.rating - pB.rating) / 400))

        quality = ts_env.quality_1vs1(tA, tB)

        rows.append(
            {
                "tourney_datetime": row["tourney_datetime"],
                "player_A_name": A,
                "player_B_name": B,
                "winner_elo": rA_e,
                "loser_elo": rB_e,
                "elo_diff": rA_e - rB_e,
                "winner_elo_exp": exp_e,
                "winner_glicko": pA.rating,
                "winner_glicko_rd": pA.rd,
                "loser_glicko": pB.rating,
                "loser_glicko_rd": pB.rd,
                "glicko_diff": pA.rating - pB.rating,
                "winner_glicko_exp": exp_g,
                "winner_ts_mu": tA.mu,
                "winner_ts_sigma": tA.sigma,
                "loser_ts_mu": tB.mu,
                "loser_ts_sigma": tB.sigma,
                "ts_quality": quality,
                "match_id": row["match_id"],
            }
        )

        K = 32
        elo[A] += K * (result - exp_e)
        elo[B] += K * ((1 - result) - (1 - exp_e))

        pA.update_player([pB.rating], [pB.rd], [result])
        pB.update_player([pA.rating], [pA.rd], [1 - result])

        if result == 1:
            new_tA, new_tB = ts_env.rate_1vs1(tA, tB)
        else:
            new_tB, new_tA = ts_env.rate_1vs1(tB, tA)
        ts_ratings[A], ts_ratings[B] = new_tA, new_tB

    return pd.DataFrame(rows)


def _invert_score_if_needed(score: str, outcome: int) -> str:
    """Inverte os sets na string de score se outcome==0."""
    if not isinstance(score, str):
        return score
    s = score.strip().upper()
    if outcome == 1 or s in {"W/O", "WO", "RET", "RETIRE"}:
        return score  # não inverte

    partes = s.split()
    invertidos = []
    for p in partes:
        m = re.match(r"(\d+)-(\d+)(\(\d+\))?$", p)
        if m:
            a, b, tb = m.groups()
            invertidos.append(f"{b}-{a}{tb or ''}")
        else:
            invertidos.append(p)
    return " ".join(invertidos)


def extract_score_features(row):
    """Retorna dict com features de score, já invertendo se necessário."""
    score = _invert_score_if_needed(row["score"], row["outcome"])
    s = score.strip().upper() if isinstance(score, str) else ""
    if s in {"W/O", "WO", "RET", "RETIRE"} or pd.isna(score):
        return {
            "score": score,
            "is_walkover": 1,
            "sets_A": np.nan,
            "sets_B": np.nan,
            "games_A": np.nan,
            "games_B": np.nan,
            "set_diff": np.nan,
            "game_diff": np.nan,
            "n_tiebreaks": np.nan,
            "pct_games_A": np.nan,
        }
    pattern = r"(\d+)-(\d+)(?:\((\d+)\))?"
    raw = re.findall(pattern, score)
    sets = [(int(a), int(b), int(tb) if tb else 0) for a, b, tb in raw]
    sets_A = sum(1 for a, b, _ in sets if a > b)
    sets_B = sum(1 for a, b, _ in sets if b > a)
    games_A = sum(a for a, _, _ in sets)
    games_B = sum(b for _, b, _ in sets)
    n_tie = sum(1 for *_, tb in sets if tb > 0)
    total_games = games_A + games_B

    return {
        "score": score,
        "is_walkover": 0,
        "sets_A": sets_A,
        "sets_B": sets_B,
        "games_A": games_A,
        "games_B": games_B,
        "set_diff": sets_A - sets_B,
        "game_diff": games_A - games_B,
        "n_tiebreaks": n_tie,
        "pct_games_A": (games_A / total_games) if total_games else np.nan,
    }


def prepare_tennis_model_data(data, score_feats):
    """
    Prepare tennis match data for modeling by:
    1. Combining match data with score features
    2. Sorting by datetime and resetting match IDs
    3. Creating player-level statistics using expanding means
    4. Merging player statistics back to the match data

    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame containing match data with columns: match_id, tourney_datetime,
        player_A_name, player_B_name, score, outcome
    score_feats : pandas.DataFrame
        DataFrame containing score-related features with match_id as index

    Returns:
    --------
    pandas.DataFrame
        Processed DataFrame ready for modeling
    """
    # Combine match data with score features
    df_feats = pd.concat(
        [
            data[
                [
                    "match_id",
                    "tourney_datetime",
                    "player_A_name",
                    "player_B_name",
                    "score",
                    "outcome",
                ]
            ],
            score_feats,
        ],
        axis=1,
    )

    # Sort by datetime and reset match IDs
    df_final = df_feats.sort_values("tourney_datetime").reset_index(drop=True)
    df_final["match_id"] = df_final.index

    # Define statistics columns to track
    stats_cols = ["sets_A", "sets_B", "games_A", "games_B", "n_tiebreaks"]

    # Create long-format DataFrame for player-level statistics
    long = pd.concat(
        [
            df_final[
                ["match_id", "tourney_datetime", "player_A_name"] + stats_cols
            ].rename(columns={"player_A_name": "player"}),
            df_final[
                ["match_id", "tourney_datetime", "player_B_name"] + stats_cols
            ].rename(columns={"player_B_name": "player"}),
        ]
    ).sort_values(["player", "tourney_datetime", "match_id"])

    # Calculate expanding averages for each statistic by player
    for c in stats_cols:
        long[f"avg_{c}"] = long.groupby("player")[c].transform(
            lambda x: x.expanding().mean().shift()
        )

    # Extract player statistics
    long_stats = long[["match_id", "player"] + [f"avg_{c}" for c in stats_cols]]

    # Merge player A statistics
    df_model = (
        df_final.merge(
            long_stats,
            left_on=["match_id", "player_A_name"],
            right_on=["match_id", "player"],
            how="left",
        )
        .rename(columns={f"avg_{c}": f"player_A_avg_{c}" for c in stats_cols})
        .drop(columns=["player"])
    )

    # Merge player B statistics
    df_model = (
        df_model.merge(
            long_stats,
            left_on=["match_id", "player_B_name"],
            right_on=["match_id", "player"],
            how="left",
        )
        .rename(columns={f"avg_{c}": f"player_B_avg_{c}" for c in stats_cols})
        .drop(columns=["player"])
    )

    # Drop unnecessary columns
    to_drop = [
        "score",
        "sets_A",
        "sets_B",
        "games_A",
        "games_B",
        "n_tiebreaks",
        "is_walkover",
        "set_diff",
        "game_diff",
        "pct_games_A",
    ]
    df_model = df_model.drop(columns=[c for c in to_drop if c in df_model.columns])

    return df_model


def finalize_tennis_model_data(data, df_model, df_features):
    """
    Finalize the tennis match data preparation by:
    1. Merging the original data with model data and feature data
    2. Removing unnecessary columns to create a clean dataset for modeling

    Parameters:
    -----------
    data : pandas.DataFrame
        Original DataFrame containing match data
    df_model : pandas.DataFrame
        Processed model DataFrame with player statistics
    df_features : pandas.DataFrame
        DataFrame containing additional features

    Returns:
    --------
    pandas.DataFrame
        Final cleaned DataFrame ready for modeling
    """
    # Merge the original data with model data
    df_final = data.merge(
        df_model,
        on=[
            "outcome",
            "match_id",
            "tourney_datetime",
            "player_A_name",
            "player_B_name",
        ],
        how="left",
    )

    # Merge with additional features
    df_final = df_final.merge(
        df_features,
        on=["match_id", "tourney_datetime", "player_A_name", "player_B_name"],
        how="left",
    )

    # Drop unnecessary columns
    columns_to_drop = [
        "tourney_name",
        "player_B_ioc",
        "player_A_ioc",
        "match_id",
        "player_A_rank_points",
        "player_A_rank",
        "player_B_rank_points",
        "player_B_rank",
        "score",
        "player_A_entry",
        "player_A_seed",
        "player_A_id",
        "player_B_entry",
        "player_B_seed",
        "player_B_id",
        "match_num",
        "tourney_id",
        "minutes",
        "player_A_ace",
        "player_A_df",
        "player_A_svpt",
        "player_A_1stIn",
        "player_A_1stWon",
        "player_A_2ndWon",
        "player_A_SvGms",
        "player_A_bpSaved",
        "player_A_bpFaced",
        "player_B_ace",
        "player_B_df",
        "player_B_svpt",
        "player_B_1stIn",
        "player_B_1stWon",
        "player_B_2ndWon",
        "player_B_SvGms",
        "player_B_bpSaved",
        "player_B_bpFaced",
        "draw_size",
    ]

    # Only drop columns that exist in the DataFrame
    df_final = df_final.drop(
        columns=[c for c in columns_to_drop if c in df_final.columns]
    )

    return df_final


def create_dummy_variables(
    df, standard_dummy_cols=None, reduced_category_config=None, cols_to_drop=None
):
    """
    Create dummy variables from categorical columns with options to:
    1. Create standard dummy variables for specified columns
    2. Reduce high-cardinality categorical columns to top N categories before creating dummies
    3. Drop specified columns after dummy creation

    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing categorical columns
    standard_dummy_cols : list, optional
        List of column names to convert directly to dummy variables
    reduced_category_config : list of tuples, optional
        List of (column_name, top_n) tuples specifying columns to reduce to top N categories
        before creating dummy variables
    cols_to_drop : list, optional
        List of column names to drop after dummy creation

    Returns:
    --------
    pandas.DataFrame
        DataFrame with dummy variables created and specified columns dropped
    """
    result_df = df.copy()

    # Step 1: Create standard dummy variables
    if standard_dummy_cols:
        result_df = pd.get_dummies(
            result_df, columns=standard_dummy_cols, drop_first=True
        )

    # Step 2: Reduce high-cardinality columns and create dummies
    if reduced_category_config:
        reduced_cols = []
        for col, n in reduced_category_config:
            # Get top N categories
            top = result_df[col].value_counts().nlargest(n).index

            # Create new column with reduced categories
            reduced_col = f"{col}_reduzido"
            result_df[reduced_col] = result_df[col].where(
                result_df[col].isin(top), "Outros"
            )
            reduced_cols.append(reduced_col)

        # Create dummies for reduced columns
        result_df = pd.get_dummies(result_df, columns=reduced_cols, drop_first=True)

    # Step 3: Drop specified columns
    if cols_to_drop:
        result_df = result_df.drop(
            columns=[c for c in cols_to_drop if c in result_df.columns]
        )

    return result_df


def scale_numerical_features(df, columns_to_scale):
    """
    Scale numerical features using MinMaxScaler.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing numerical columns to scale
    columns_to_scale : list
        List of column names to scale

    Returns:
    --------
    pandas.DataFrame
        DataFrame with scaled numerical features
    """
    # Create a copy of the input DataFrame to avoid modifying the original
    result_df = df.copy()

    # Initialize the MinMaxScaler
    scaler = MinMaxScaler()

    # Apply scaling to the specified columns
    result_df[columns_to_scale] = scaler.fit_transform(result_df[columns_to_scale])

    return result_df
