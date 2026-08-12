"""
monthly_analysis.py
Orchestrates the per-month pipeline: load -> clean -> engineer -> summarize.
Produces the monthly_summary analytical dataset (Phase 9) used for
month-over-month comparison visuals (Phase 2).
"""

import pandas as pd

from data_loader import load_month
from preprocessing import clean_trips
from feature_engineering import add_features

SUMMARY_METRICS = [
    "year", "month", "trip_count", "total_revenue",
    "avg_fare", "avg_tip", "avg_total", "tip_pct_of_trips",
    "avg_trip_distance", "avg_trip_duration_min", "avg_speed_mph",
]


def process_month(year: int, month: int) -> tuple[pd.DataFrame, dict]:
    """Full single-month pipeline. Returns (featured_df, clean_report)."""
    raw = load_month(year, month)
    clean, clean_report = clean_trips(raw)
    featured = add_features(clean)
    return featured, clean_report


def summarize_month(df: pd.DataFrame, year: int, month: int) -> dict:
    """One row of monthly_summary metrics from an already featured DataFrame."""
    return {
        "year": year,
        "month": month,
        "trip_count": len(df),
        "total_revenue": round(df["total_amount"].sum(), 2),
        "avg_fare": round(df["fare_amount"].mean(), 2),
        "avg_tip": round(df["tip_amount"].mean(), 2),
        "avg_total": round(df["total_amount"].mean(), 2),
        "tip_pct_of_trips": round(100 * df["is_tipped"].mean(), 2),
        "avg_trip_distance": round(df["trip_distance"].mean(), 2),
        "avg_trip_duration_min": round(df["trip_duration_min"].mean(), 2),
        "avg_speed_mph": round(df["average_speed_mph"].mean(), 2),
    }


def build_monthly_summary(year: int, months: range = range(1, 13)) -> pd.DataFrame:
    """Run pipeline across all requested months, return one row per month."""
    rows = []
    for m in months:
        featured, _ = process_month(year, m)
        rows.append(summarize_month(featured, year, m))
    return pd.DataFrame(rows, columns=SUMMARY_METRICS)


if __name__ == "__main__":
    summary = build_monthly_summary(2025, range(1, 13))
    print(summary.to_string(index=False))
