"""
visualization.py
Reusable plot functions for the NYC taxi analysis. One function per chart
TYPE (not per specific chart) — callers pass data/columns to reuse across
monthly, hourly, financial, geospatial, and anomaly sections.

All functions return a matplotlib Figure. Caller decides show/save.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")
FIGSIZE_WIDE = (12, 5)
FIGSIZE_SQUARE = (8, 6)


def plot_monthly_trend(summary_df: pd.DataFrame, metric: str, title: str = None, ylabel: str = None) -> plt.Figure:
    """Line chart of one metric across months. summary_df must have 'month' and metric columns."""
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.plot(summary_df["month"], summary_df[metric], marker="o", linewidth=2)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("Month")
    ax.set_ylabel(ylabel or metric)
    ax.set_title(title or f"{metric} by Month")
    fig.tight_layout()
    return fig


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str = None, top_n: int = None) -> plt.Figure:
    """Generic bar chart. Used for hourly demand, weekday demand, top zones, payment type."""
    d = df.sort_values(y, ascending=False).head(top_n) if top_n else df
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.bar(d[x].astype(str), d[y])
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title or f"{y} by {x}")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return fig


def plot_heatmap(pivot_df: pd.DataFrame, title: str = None, fmt: str = ".0f") -> plt.Figure:
    """Generic heatmap. Used for weekday x hour, month x hour demand grids."""
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    sns.heatmap(pivot_df, annot=False, cmap="viridis", fmt=fmt, ax=ax)
    ax.set_title(title or "Heatmap")
    fig.tight_layout()
    return fig


def plot_distribution(df: pd.DataFrame, column: str, bins: int = 50, clip_upper_pct: float = 0.99) -> plt.Figure:
    """Histogram, clipped at upper percentile so extreme outliers don't flatten the shape."""
    upper = df[column].quantile(clip_upper_pct)
    data = df[df[column] <= upper][column]
    fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
    ax.hist(data, bins=bins, edgecolor="black", alpha=0.75)
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of {column} (clipped at p{int(clip_upper_pct*100)})")
    fig.tight_layout()
    return fig


def plot_boxplot(df: pd.DataFrame, column: str, by: str = None) -> plt.Figure:
    """Boxplot, optionally grouped by a categorical column."""
    fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
    if by:
        df.boxplot(column=column, by=by, ax=ax)
        plt.suptitle("")
        ax.set_title(f"{column} by {by}")
    else:
        ax.boxplot(df[column].dropna(), vert=True)
        ax.set_title(f"Boxplot of {column}")
    fig.tight_layout()
    return fig


def plot_scatter(df: pd.DataFrame, x: str, y: str, sample: int = 5000, alpha: float = 0.3) -> plt.Figure:
    """Scatter with sampling for large datasets (e.g. distance vs fare)."""
    d = df.sample(min(sample, len(df)), random_state=42)
    fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
    ax.scatter(d[x], d[y], alpha=alpha, s=10)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"{y} vs {x}")
    fig.tight_layout()
    return fig


def plot_correlation_matrix(df: pd.DataFrame, columns: list[str]) -> plt.Figure:
    """Correlation heatmap for a set of numeric columns."""
    corr = df[columns].corr()
    fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Matrix")
    fig.tight_layout()
    return fig


def save_fig(fig: plt.Figure, path: str, dpi: int = 150) -> None:
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
