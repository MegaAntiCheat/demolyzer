"""Module for Computing Aggregates of the Converted DataFrame of demo File."""

import os
import random
from math import atan2#, degrees
from functools import cached_property

import pandas as pd

from demolyzer.demo_utils import demo_to_dataframe


def _normalize_angle(angle: int | float) -> float:
    return (angle + 180) % 360 - 180


def replace_player_ids_with_steamid(df: pd.DataFrame) -> pd.DataFrame:
    """Replace player IDs in the dataframe with their corresponding Steam IDs."""

    steamid_mapping = (
        df.drop_duplicates("players_info.userId", keep="last")
        .set_index("players_info.userId")["players_info.steamId"]
        .to_dict()
    )

    df["kills_assister_id"] = df["kills_assister_id"].map(steamid_mapping).fillna(df["kills_assister_id"])
    df["kills_attacker_id"] = df["kills_attacker_id"].map(steamid_mapping).fillna(df["kills_attacker_id"])
    df["kills_victim_id"] = df["kills_victim_id"].map(steamid_mapping).fillna(df["kills_victim_id"])

    return df


class DemoAnalyzer:
    def __init__(self, demo_in_path: str, persist: bool = True, tick_frequency: int = 100):
        """Initialize an instance of a DemoAnalyzer.

        Args:
            demo_in_path: Path to demo file.
            persist: Persist converted demo as a csv as to not re-convert. Defaults to True.
            tick_frequency: tick frequency arg passed into demoreel. Defaults to 100.
        """
        csv_name = f"{os.path.splitext(demo_in_path)[0]}.csv"
        if persist and os.path.exists(csv_name):
            self.df = pd.read_csv(csv_name)
        else:
            self.df = demo_to_dataframe(demo_in_path, tick_frequency)
            if persist:
                self.df.to_csv(csv_name, index=False)

        self.demo_file = demo_in_path

    @cached_property
    def players(self) -> dict[str, str]:
        """Get the players in this file.

        Returns:
            dict of {steam_id: player_name}
        """
        unique_ids_df = self.df.drop_duplicates(subset="players_info.steamId")

        players = dict(zip(unique_ids_df["players_info.steamId"], unique_ids_df["players_info.name"]))

        return players

    @cached_property
    def num_players(self) -> int:
        """Get the number of players in this demo file.

        Returns:
            number of players
        """
        return len(self.df["players_info.steamId"].unique())

    @cached_property
    def duration(self) -> float:
        pass

    def death_stats(self) -> dict[str, dict[str, float | int]]:
        """Get the number of alive and death ticks for all players in a given demo.

        Returns:
            dict of {steam_id: {alive_ticks: int, death_ticks: int}}
        """
        stats = {}
        for steam_id, name in self.players.items():
            if pd.isna(steam_id):
                continue
            player_df = self.df[self.df["players_info.steamId"] == steam_id]
            tick_stats = player_df["players_state"].value_counts().to_dict()
            stats[steam_id] = {
                "alive_ticks": tick_stats.get("Alive", None),
                "death_ticks": tick_stats.get("Death", None),
            }

        return stats

    def get_event_dataframe(self, ticks_before: int = 100, ticks_after: int = 100) -> pd.DataFrame():
        """Return a dataframe that each contains events around a shooting or damage event.

        Args:
            ticks_before: ticks before event to keep in that event.
            ticks_after: ticks after event to keep in that event.

        Returns:
            Event dataframe with new event_id column for an entire event involving each player shooting another.
        """

        df = replace_player_ids_with_steamid(self.df.copy())
        unique_combinations = df[["kills_attacker_id", "kills_victim_id"]].drop_duplicates().dropna()

        event_dataframes = []
        event_id = 0
        for _, row in unique_combinations.iterrows():
            attacker_steamId = row["kills_attacker_id"]
            victim_steamId = row["kills_victim_id"]
            filtered_df = df[(df["kills_attacker_id"] == attacker_steamId) | (df["kills_victim_id"] == victim_steamId)]

            shooting_events = filtered_df[
                (filtered_df["kills_attacker_id"] == attacker_steamId)
                & (filtered_df["kills_victim_id"] == victim_steamId)
            ].copy()

            for _, shooting_event in shooting_events.iterrows():
                shooting_tick = shooting_event["tick"]
                start_tick = shooting_tick - ticks_before
                end_tick = shooting_tick + ticks_after

                event_df = df[
                    (df["tick"] >= start_tick)
                    & (df["tick"] <= end_tick)
                    & (df["players_info.steamId"] == attacker_steamId)
                ].copy()
                event_df["event_id"] = event_id
                event_dataframes.append(event_df)
                event_id += 1

        combined = pd.concat(event_dataframes)
        return combined

    def __str__(self) -> str:
        return f"{self.demo_file} with {self.num_players} players and duration of {self.duration}"
