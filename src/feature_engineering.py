"""
feature_engineering.py
Derive analysis features from cleaned trip data. One canonical function.

Adds: trip_duration_min, average_speed_mph, fare_per_mile, tip_rate,
pickup_hour, pickup_dow, pickup_dow_name, is_weekend, is_tipped.
Assumes input already passed preprocessing.clean_trips (no missing/invalid core fields).
"""

import pandas as pd

REQUIRED_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "fare_amount",
    "tip_amount",
    "total_amount",
]


def _validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    _validate_schema(df)
    d = df.copy()

    # temporal
    d["trip_duration_min"] = (
        d["tpep_dropoff_datetime"] - d["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    d["pickup_hour"] = d["tpep_pickup_datetime"].dt.hour
    d["pickup_dow"] = d["tpep_pickup_datetime"].dt.dayofweek  # 0=Mon
    d["pickup_dow_name"] = d["tpep_pickup_datetime"].dt.day_name()
    d["is_weekend"] = d["pickup_dow"] >= 5

    # speed: guard divide-by-zero explicitly (duration validated > 0 upstream, but be explicit)
    if (d["trip_duration_min"] <= 0).any():
        raise ValueError("trip_duration_min contains non-positive values; run preprocessing.clean_trips first")
    d["average_speed_mph"] = d["trip_distance"] / (d["trip_duration_min"] / 60)

    # financial
    d["fare_per_mile"] = d["fare_amount"] / d["trip_distance"]
    d["tip_rate"] = d["tip_amount"] / d["fare_amount"]
    d["is_tipped"] = d["tip_amount"] > 0

    return d


if __name__ == "__main__":
    from data_loader import load_month
    from preprocessing import clean_trips

    raw = load_month(2025, 1)
    clean, _ = clean_trips(raw)
    featured = add_features(clean)
    print(featured[["trip_duration_min", "average_speed_mph", "fare_per_mile", "tip_rate"]].describe())
