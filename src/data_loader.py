"""
data_loader.py
Fetch and cache NYC Yellow Taxi monthly trip data (2025) from NYC TLC CloudFront source.

One path only: download if not cached, then read parquet. No silent fallbacks.
Raises on any failure (bad month, HTTP error, empty/corrupt file).
"""

from pathlib import Path
import zipfile
import requests
import pandas as pd

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
ZONE_SHAPES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
TIMEOUT_SECONDS = 120


def _validate_month(month: int) -> None:
    if not (1 <= month <= 12):
        raise ValueError(f"month must be 1-12, got {month}")


def _local_path(year: int, month: int) -> Path:
    return RAW_DIR / f"yellow_tripdata_{year}-{month:02d}.parquet"


def download_month(year: int, month: int, force: bool = False) -> Path:
    """Download one month's parquet to local cache. Returns local file path."""
    _validate_month(month)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = _local_path(year, month)

    if dest.exists() and not force:
        return dest

    url = BASE_URL.format(year=year, month=month)
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    if response.status_code != 200:
        raise RuntimeError(f"download failed: {url} status={response.status_code}")

    dest.write_bytes(response.content)
    if dest.stat().st_size == 0:
        dest.unlink()
        raise RuntimeError(f"downloaded file empty: {url}")

    return dest


def load_month(year: int, month: int, force: bool = False) -> pd.DataFrame:
    """Load one month as DataFrame, tagged with year/month columns."""
    path = download_month(year, month, force=force)
    df = pd.read_parquet(path)
    if df.empty:
        raise RuntimeError(f"parquet has zero rows: {path}")

    df["data_year"] = year
    df["data_month"] = month
    return df


def load_year(year: int, months: range = range(1, 13), force: bool = False) -> pd.DataFrame:
    """Load and concatenate all requested months for a year into one DataFrame."""
    frames = [load_month(year, m, force=force) for m in months]
    return pd.concat(frames, ignore_index=True)


def load_zone_lookup(force: bool = False) -> pd.DataFrame:
    """Load NYC TLC taxi zone lookup (LocationID -> Borough, Zone, service_zone)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / "taxi_zone_lookup.csv"

    if not dest.exists() or force:
        response = requests.get(ZONE_LOOKUP_URL, timeout=TIMEOUT_SECONDS)
        if response.status_code != 200:
            raise RuntimeError(
                f"download failed: {ZONE_LOOKUP_URL} status={response.status_code}"
            )
        dest.write_bytes(response.content)

    df = pd.read_csv(dest)

    if df.empty:
        raise RuntimeError(f"zone lookup has zero rows: {dest}")

    return df


def load_zone_shapes(force: bool = False):
    """Load NYC TLC taxi zone polygon geometry (LocationID -> Zone, Borough, geometry),
    reprojected to WGS84 (EPSG:4326) for direct use with folium/matplotlib map plotting.
    Requires geopandas -- imported locally so notebooks that don't map aren't forced to
    install it."""
    try:
        import geopandas as gpd  # type: ignore
    except Exception as e:  # pragma: no cover - dependency availability
        raise RuntimeError(
            "geopandas is required for load_zone_shapes; install it (e.g. 'pip install geopandas')"
        ) from e

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest_zip = RAW_DIR / "taxi_zones.zip"
    extract_dir = RAW_DIR / "taxi_zones"

    if not dest_zip.exists() or force:
        response = requests.get(ZONE_SHAPES_URL, timeout=TIMEOUT_SECONDS)
        if response.status_code != 200:
            raise RuntimeError(f"download failed: {ZONE_SHAPES_URL} status={response.status_code}")
        dest_zip.write_bytes(response.content)

    if not extract_dir.exists() or force:
        with zipfile.ZipFile(dest_zip) as zf:
            zf.extractall(extract_dir)

    shp_files = list(extract_dir.rglob("*.shp"))
    if not shp_files:
        raise RuntimeError(f"no .shp file found after extracting {dest_zip}")

    gdf = gpd.read_file(shp_files[0])
    gdf = gdf.rename(columns={"zone": "Zone", "borough": "Borough"})
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    if gdf.empty:
        raise RuntimeError(f"zone shapefile has zero rows: {shp_files[0]}")
    return gdf


if __name__ == "__main__":
    data = load_year(2025, range(1, 13))
    print(f"loaded rows={len(data)} months={sorted(data['data_month'].unique())}")
