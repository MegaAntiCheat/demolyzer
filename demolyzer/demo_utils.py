"""Module for utilities for."""

from typing import Any

import demoreel
import pandas as pd

NORMALIZED_KEYS = ("tick", "world")


def convert_demo(demo_in_path: str, tick_frequency: int = 100) -> list[dict[str, Any]]:
    """Convert a demo file using demoreel.

    Args:
        demo_in_path: path to the demo file to convert.
        tick_frequency: tick frequency arg passed into demoreel. Defaults to 100.

    Returns:
        converted demo object
    """
    with open(demo_in_path, "rb") as f:
        demo_file = f.read()

    # note that this is currently json and is subject to change
    converted = demoreel.unspool(demo_file, tick_freq=tick_frequency)

    return converted


def normalize_nested_field(field: str, field_data: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize a nested field into a dataframe.

    Args:
        field: name of the nested field.
        field_data: data for that nested field.

    Returns:
        flattened/normalized dataframe for that field's data.
    """
    normalized = pd.json_normalize(field_data)
    normalized.columns = [f"{field}_{col}" for col in normalized.columns]

    return normalized


def to_dataframe(demo_data: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert parsed demo data into a useable dataframe.

    Args:
        demo_data: demo data to parse.

    Returns:
        dataframe of demo data suited for analysis.
    """
    dfs = []
    for nested_row in demo_data:
        keys_to_normalize = [key for key in list(nested_row.keys()) if key not in NORMALIZED_KEYS]
        to_concat = []
        for key in keys_to_normalize:
            normalized_key = normalize_nested_field(key, nested_row[key])
            to_concat.append(normalized_key)

        row_df = pd.concat(to_concat)
        for key in NORMALIZED_KEYS:
            row_df[key] = nested_row[key]

        dfs.append(row_df)

    df = pd.concat(dfs).sort_values(by="tick")
    ordered_cols = ["tick"] + sorted([col for col in df.columns if col != "tick"])
    df = df[ordered_cols]

    # Add the copy() method
    df = df.copy()

    return df


def demo_to_dataframe(demo_in_path: str, tick_frequency: int = 100) -> pd.DataFrame:
    """Turn a demo file into a sparse wide csv file.

    Args:
        demo_path: path to the demo file.
        tick_frequency: tick frequency arg passed into demoreel. Defaults to 100.

    Returns:
        dataframe ready to be analyzed downstream.
    """
    demo_data = convert_demo(demo_in_path, tick_frequency)
    demo_df = to_dataframe(demo_data)

    return demo_df
