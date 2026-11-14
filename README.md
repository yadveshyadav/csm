# CMS Hospital Readmissions Analysis

A portfolio project using the CMS Hospital Readmissions Reduction Program (HRRP) dataset to investigate:

> **Which hospital-condition measures show higher-than-expected 30-day readmissions, and how should leaders prioritize follow-up?**

The project demonstrates Python/pandas data cleaning, PostgreSQL loading and SQL analysis, a descriptive regression, Tableau dashboard development, and a client-style insight memo.

## Published visualization

[Open the Tableau Public workbook](https://public.tableau.com/app/profile/yadvesh.yadav/viz/Book1_17946471423360/Sheet4). It currently contains four sheets; this link opens Sheet 4, and the workbook tabs lead to the other sheets.

## Data

Source: [CMS Hospital Readmissions Reduction Program](https://data.cms.gov/provider-data/dataset/9n3s-kdb3). The CMS catalog currently describes 18,330 rows and 12 columns (checked November 14, 2026); use the live page for the latest release. Fields include hospital, state, condition/measure, discharges, predicted and expected readmission rates, and excess readmission ratio. CMS calculates expected readmissions based on similar patients.

The script downloads the published CSV at runtime. Raw and cleaned data files are excluded from Git. Small derived summary tables are included under `outputs/`; no patient-level data is present. The pipeline fails with a useful message if CMS changes the schema.

## Setup

Requires Python 3.10+ and PostgreSQL 14+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create an empty PostgreSQL database named `CSRM`, then set a connection string for your local installation. Replace the placeholder locally; never commit a real password:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/CSRM"
python src/pipeline.py
```

The script writes cleaned rows into `hrrp_hospital_measure` and creates `outputs/by_measure.csv`, `outputs/by_state.csv`, `outputs/model_summary.txt`, and `outputs/data_quality.txt`.

## Results snapshot

The analyzed CMS reporting period is July 1, 2021–June 30, 2024. The load contains 18,330 hospital-measure rows, 3,055 facilities, and six measures. Ratios were unavailable for 6,610 rows.

| CMS measure | Hospitals with reported ratio | Median excess ratio | Share above 1.0 |
|---|---:|---:|---:|
| AMI | 1,736 | 0.9995 | 49.7% |
| CABG | 878 | 1.0000 | 49.9% |
| COPD | 2,323 | 0.9969 | 47.2% |
| Heart failure | 2,621 | 0.9983 | 48.9% |
| Hip/knee replacement | 1,447 | 0.9916 | 47.9% |
| Pneumonia | 2,715 | 0.9955 | 46.8% |

The complete-case descriptive regression uses 8,037 rows, has R-squared 0.024, and estimates a negative association between discharge volume and excess ratio (HC3 robust p < 0.001). See [`memo/insights.md`](memo/insights.md) for interpretation and limitations; this is not a causal or patient-level model.

To download and analyze without PostgreSQL:

```powershell
python src/pipeline.py --skip-db
```

To fetch a fresh CMS copy, use `python src/pipeline.py --force-download` (add `--skip-db` if needed).

Run the queries in [`sql/analysis.sql`](sql/analysis.sql) in pgAdmin or `psql`.

## Statistical model

The pipeline fits ordinary least squares with HC3 robust standard errors: excess readmission ratio is modeled against discharge volume and measure/condition. This is a descriptive association using CMS-published aggregate statistics. It does not establish causes, predict patient outcomes, or independently adjust for patient case mix. Do not treat hospital rows as a definitive quality ranking.

## Tableau

Tableau Public connects to supported files rather than directly to PostgreSQL. Export the loaded table to CSV from `psql`, then open the CSV in Tableau using **Text file**. For a direct PostgreSQL connector, use a Tableau Desktop edition that supports database connections. Follow [`tableau/dashboard-notes.md`](tableau/dashboard-notes.md) to build and publish the views.

## Memo and findings

The one-page [`memo/insights.md`](memo/insights.md) summarizes three observed findings, a recommendation, and the main data and model limitations.

## Interpretation notes

- The CMS excess readmission ratio compares predicted with expected readmissions; a value above 1 indicates predicted readmissions exceed expected for that measure.
- Do not convert `N/A` or `Too Few to Report` into zero; the pipeline keeps these values missing.
- Report the exact CMS release/reporting period used. The upstream catalog can change.
- CMS aggregate data describes outcomes but does not tell you why a patient returned to hospital.
