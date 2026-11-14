"""Download, clean, load, and analyze the CMS HRRP public dataset."""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import pandas as pd
import requests
from sqlalchemy import create_engine, text

DATASET_PAGE = "https://data.cms.gov/provider-data/dataset/9n3s-kdb3"
# Current CMS catalog distribution (FY 2026 release). Update if CMS rotates it.
DATA_URL = (
    "https://data.cms.gov/provider-data/sites/default/files/resources/"
    "a171bc36c488d3e0dc33ec63abb469a6_1770163617/"
    "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
)
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "hrrp.csv"

RENAME = {
    "facility name": "facility_name", "facility id": "facility_id",
    "state": "state", "measure name": "measure_name",
    "number of discharges": "discharges", "footnote": "footnote",
    "excess readmission ratio": "excess_ratio",
    "predicted readmission rate": "predicted_rate",
    "expected readmission rate": "expected_rate",
    "number of readmissions": "readmissions",
    "start date": "start_date", "end date": "end_date",
}
NUMERIC = ["discharges", "excess_ratio", "predicted_rate", "expected_rate", "readmissions"]


def download(force: bool = False) -> Path:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists() and not force:
        return RAW
    response = requests.get(DATA_URL, timeout=120)
    response.raise_for_status()
    RAW.write_bytes(response.content)
    return RAW


def clean(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, low_memory=False)
    df.columns = [re.sub(r"\s+", " ", str(c).strip().lower()) for c in df.columns]
    missing = set(RENAME) - set(df.columns)
    if missing:
        raise ValueError(f"CMS file schema changed; missing columns: {sorted(missing)}. See {DATASET_PAGE}")
    df = df.rename(columns=RENAME)
    df["facility_id"] = df["facility_id"].str.strip().str.zfill(6)
    df["state"] = df["state"].str.strip().str.upper()
    df["facility_name"] = df["facility_name"].str.strip()
    df["measure_name"] = df["measure_name"].str.strip()
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col].str.strip().replace({"N/A": None, "Too Few to Report": None, "": None}), errors="coerce")
    for col in ("start_date", "end_date"):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    df["footnote"] = df["footnote"].fillna("").str.strip()
    df = df.drop_duplicates(subset=["facility_id", "measure_name", "start_date", "end_date"])
    return df


def load(df: pd.DataFrame, database_url: str) -> None:
    engine = create_engine(database_url)
    df.to_sql("hrrp_hospital_measure", engine, if_exists="replace", index=False, method="multi", chunksize=1000)
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_hrrp_state ON hrrp_hospital_measure (state)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_hrrp_measure ON hrrp_hospital_measure (measure_name)"))


def analyze(df: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    valid = df.dropna(subset=["excess_ratio"]).copy()
    # Descriptive OLS on records with observed ratio and volume; not a new case-mix adjustment.
    import statsmodels.formula.api as smf
    model_data = valid.dropna(subset=["discharges", "measure_name"])
    model = smf.ols("excess_ratio ~ discharges + C(measure_name)", data=model_data).fit(cov_type="HC3")
    (output / "model_summary.txt").write_text(model.summary().as_text(), encoding="utf-8")
    by_measure = valid.groupby("measure_name", as_index=False).agg(
        hospitals=("facility_id", "nunique"), median_excess_ratio=("excess_ratio", "median"),
        share_above_1=("excess_ratio", lambda s: (s > 1).mean()), median_discharges=("discharges", "median")
    )
    by_measure.to_csv(output / "by_measure.csv", index=False)
    state = valid.groupby("state", as_index=False).agg(hospitals=("facility_id", "nunique"), median_excess_ratio=("excess_ratio", "median"))
    state.to_csv(output / "by_state.csv", index=False)
    (output / "data_quality.txt").write_text(
        f"Rows after deduplication: {len(df)}\nFacilities: {df.facility_id.nunique()}\n"
        f"Measures: {df.measure_name.nunique()}\nRows without excess ratio: {df.excess_ratio.isna().sum()}\n"
        f"Source: {DATASET_PAGE}\nDownload file: {RAW.name}\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--skip-db", action="store_true", help="Analyze without PostgreSQL")
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    args = parser.parse_args()
    path = download(args.force_download)
    df = clean(path)
    if not args.skip_db:
        if not args.database_url:
            raise SystemExit("Set DATABASE_URL or use --skip-db. Example: postgresql+psycopg://user:password@localhost:5432/hrrp")
        load(df, args.database_url)
    analyze(df, ROOT / "outputs")
    print(f"Processed {len(df):,} records; outputs saved under outputs/")


if __name__ == "__main__":
    main()
