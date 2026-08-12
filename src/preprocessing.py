"""
preprocessing.py
Clean raw NYC Yellow Taxi trip records. One canonical cleaning path.

Scope: dtype fixes, missing values, duplicates, invalid/impossible records.
Does NOT engineer new features (see feature_engineering.py).
Returns cleaned DataFrame + a quality report (counts removed per rule), so
every drop is traceable.
"""

import pandas as pd

REQUIRED_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "total_amount",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "data_year",
    "data_month",
]


def _validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def clean_trips(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean one month (or multi-month) trip DataFrame. Returns (clean_df, report)."""
    _validate_schema(df)
    report = {"input_rows": len(df)}
    d = df.copy()

    # dtypes
    d["tpep_pickup_datetime"] = pd.to_datetime(d["tpep_pickup_datetime"])
    d["tpep_dropoff_datetime"] = pd.to_datetime(d["tpep_dropoff_datetime"])

    # duplicates
    before = len(d)
    d = d.drop_duplicates()
    report["duplicates_removed"] = before - len(d)

    # missing values in critical columns -> drop (no imputation on core fields)
    before = len(d)
    critical = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance",
                "fare_amount", "total_amount", "PULocationID", "DOLocationID"]
    d = d.dropna(subset=critical)
    report["missing_critical_removed"] = before - len(d)

    # passenger_count missing -> fill 1 (median trip has 1 passenger), flag explicitly
    d["passenger_count"] = d["passenger_count"].fillna(1).astype(int)

    # pickup must precede dropoff, both within stated data_year/data_month
    before = len(d)
    d = d[d["tpep_dropoff_datetime"] > d["tpep_pickup_datetime"]]
    report["non_positive_duration_removed"] = before - len(d)

    before = len(d)
    d = d[
        (d["tpep_pickup_datetime"].dt.year == d["data_year"])
        & (d["tpep_pickup_datetime"].dt.month == d["data_month"])
    ]
    report["outside_stated_month_removed"] = before - len(d)

    # non-physical financial/distance values
    before = len(d)
    d = d[(d["fare_amount"] > 0) & (d["total_amount"] > 0) & (d["trip_distance"] > 0)]
    report["non_positive_value_removed"] = before - len(d)

    # passenger_count sanity (NYC taxi max ~6)
    before = len(d)
    d = d[(d["passenger_count"] >= 1) & (d["passenger_count"] <= 6)]
    report["invalid_passenger_count_removed"] = before - len(d)

    report["output_rows"] = len(d)
    report["total_removed"] = report["input_rows"] - report["output_rows"]
    report["removed_pct"] = round(100 * report["total_removed"] / report["input_rows"], 2)

    return d.reset_index(drop=True), report


if __name__ == "__main__":
    from data_loader import load_month

    raw = load_month(2025, 1)
    clean, rep = clean_trips(raw)
    print(rep)
