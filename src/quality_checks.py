"""
quality_checks.py
Diagnose data quality on raw or cleaned trip data. Read-only: reports issues,
never mutates or fixes (fixing belongs to preprocessing.py).
"""

import pandas as pd

NUMERIC_CHECK_COLS = ["trip_distance", "fare_amount", "tip_amount", "total_amount", "passenger_count"]


def check_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Missing value count and pct per column."""
    n = len(df)
    missing = df.isna().sum()
    out = pd.DataFrame({"missing_count": missing, "missing_pct": (100 * missing / n).round(2)})
    return out[out["missing_count"] > 0].sort_values("missing_count", ascending=False)


def check_duplicates(df: pd.DataFrame) -> dict:
    dup_count = df.duplicated().sum()
    return {
        "duplicate_rows": int(dup_count),
        "duplicate_pct": round(100 * dup_count / len(df), 2),
    }


def check_value_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Flag non-physical values: negative/zero fare, distance, total; passenger_count out of [1,6]."""
    rules = {
        "fare_amount_non_positive": (df["fare_amount"] <= 0).sum(),
        "total_amount_non_positive": (df["total_amount"] <= 0).sum(),
        "trip_distance_non_positive": (df["trip_distance"] <= 0).sum(),
        "passenger_count_invalid": (~df["passenger_count"].between(1, 6)).sum(),
    }
    n = len(df)
    return pd.DataFrame({
        "rule": list(rules.keys()),
        "violation_count": list(rules.values()),
        "violation_pct": [round(100 * v / n, 2) for v in rules.values()],
    })


def check_outliers_iqr(df: pd.DataFrame, columns: list[str] = None, k: float = 1.5) -> pd.DataFrame:
    """IQR-based outlier count per numeric column. Statistical flags only, not removal."""
    columns = columns or NUMERIC_CHECK_COLS
    rows = []
    for col in columns:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        low, high = q1 - k * iqr, q3 + k * iqr
        outliers = ((df[col] < low) | (df[col] > high)).sum()
        rows.append({
            "column": col, "q1": q1, "q3": q3, "iqr": iqr,
            "lower_bound": low, "upper_bound": high,
            "outlier_count": int(outliers),
            "outlier_pct": round(100 * outliers / len(df), 2),
        })
    return pd.DataFrame(rows)


def check_class_balance(df: pd.DataFrame, column: str) -> pd.DataFrame:
    counts = df[column].value_counts(dropna=False)
    return pd.DataFrame({"count": counts, "pct": (100 * counts / len(df)).round(2)})


def run_quality_report(df: pd.DataFrame) -> dict:
    """Aggregate all checks into one report dict."""
    return {
        "row_count": len(df),
        "missing": check_missing(df),
        "duplicates": check_duplicates(df),
        "value_range_violations": check_value_ranges(df),
        "outliers_iqr": check_outliers_iqr(df),
        "payment_type_balance": check_class_balance(df, "payment_type") if "payment_type" in df.columns else None,
    }


if __name__ == "__main__":
    from data_loader import load_month

    raw = load_month(2025, 1)
    report = run_quality_report(raw)
    print(f"rows={report['row_count']}")
    print(report["duplicates"])
    print(report["value_range_violations"])
