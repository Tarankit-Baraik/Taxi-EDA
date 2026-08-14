## NYC-Urban-Mobility-EDA
### NYC 2025 Yellow Taxi — Data Quality, Mobility & Anomaly Analysis
#### Multidimensional Urban Mobility & Financial EDA
End-to-end analysis of 12 months (48.7M raw trips) of NYC Yellow Taxi records: data
quality auditing, mobility and demand patterns, financial and payment behavior,
geospatial concentration, and statistical anomaly detection — consolidated into a
single analytical narrative with business recommendations.

## What this project does

Six notebooks, run in order, take raw monthly TLC trip files to a final,
cross-validated set of findings:

| # | Notebook | Answers |
|---|----------|---------|
| 01 | `data_ingestion_quality.ipynb` | Is the raw data reliable? Schema, missing values, duplicates, invalid records, outlier bounds, payment-code audit. Produces the cleaning spec. |
| 02 | `monthly_mobility_analysis.ipynb` | How does demand change month to month? Seasonality, peak/decline detection, monthly metric correlations. |
| 03 | `full_year_mobility_eda.ipynb` | Full-year demand by hour/weekday/month, trip distance/duration/speed distributions, fare-distance relationship. |
| 04 | `financial_payment_eda.ipynb` | Fare formation, tipping behavior, payment-method differences, tolls and surcharges. |
| 05 | `geospatial_mobility_analysis.ipynb` | Where demand concentrates: pickup/dropoff hotspots, origin-destination flows, zone-level economics, weekday/weekend zone mix. |
| 06 | `anomaly_analysis_and_insights.ipynb` | Statistical outlier detection (IQR + multivariate), geographic/temporal clustering of anomalies, and the final cross-notebook Analytical Story. |

**Key results:** 43,921,426 trips after cleaning (90.15% retention); demand peaks in
May and troughs in August; distance explains only 1.1% of fare variance linearly
(R² = 0.011) despite a strong monotonic relationship (Spearman ρ = 0.871); Manhattan
accounts for 86% of pickups; 15.24% of trips are flagged by at least one anomaly rule,
with airport zones (JFK, LaGuardia) flagged at 90%+ due to a citywide distance
threshold that doesn't account for legitimately long airport trips. Full findings are
in Notebook 06, Section 8.

## Repository structure

```
├── notebooks/
│   ├── 01_data_ingestion_quality.ipynb
│   ├── 02_monthly_mobility_analysis.ipynb
│   ├── 03_full_year_mobility_eda.ipynb
│   ├── 04_financial_payment_eda.ipynb
│   ├── 05_geospatial_mobility_analysis.ipynb
│   └── 06_anomaly_analysis_and_insights.ipynb
├── src/
│   ├── data_loader.py          # load_month, load_zone_lookup, load_zone_shapes
│   ├── preprocessing.py        # clean_trips
│   ├── feature_engineering.py  # add_features
│   ├── quality_checks.py       # check_missing, check_duplicates, check_outliers_iqr, ...
│   ├── monthly_analysis.py     # build_monthly_summary, process_month
│   └── visualization.py        # plot_bar, plot_heatmap, save_fig
├── data/
│   ├── raw/                    # monthly TLC trip files + zone lookup/shapefile (not tracked)
│   ├── processed/              # aggregation tables written by notebook 06
│   └── outputs/                # saved chart images
├── requirements.txt
└── README.md
```

## Rendered HTML Notebooks

The `rendered_html_notebooks/` folder contains the **executed HTML versions of the Jupyter notebooks**, allowing you to view the complete analysis, outputs, and visualizations directly without running the workflow yourself.
For **full project replication**, follow the procedures and setup instructions provided in the sections below.

## How to run

Requires Python >=3.9.

**1. Create and activate a virtual environment**

macOS / Linux:
```bash
python -m venv venv
source venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Windows (cmd.exe):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add the data**

No manual download needed — `src/data_loader.py` fetches each month directly from the
NYC TLC CloudFront source on first use and caches it under `data/raw/`. To pre-populate
the cache instead, run:

```bash
python -m src.data_loader
```

**4. Run the notebooks in order**

```bash
cd notebooks
jupyter notebook
```

Run `01` through `06` sequentially — each later notebook assumes the cleaning rules
established in `01` and, in places, references figures from earlier notebooks. Each
notebook processes one month at a time (load → clean → feature-engineer → aggregate →
discard) rather than holding the full year in memory at once, so no step requires more
than a few GB of RAM.

**5. Outputs**

Aggregated CSVs land in `data/processed/`; charts land in `data/outputs/`. Notebook 06
is the final deliverable — its last section is a self-contained summary of every
finding across the project.

## Data source

NYC TLC Yellow Taxi Trip Records, 2025, published by the NYC Taxi & Limousine
Commission.
