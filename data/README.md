# Source data

The pipeline downloads the current CMS Hospital Readmissions Reduction Program (HRRP) CSV from `src/pipeline.py` when run. The file is intentionally excluded from Git because it is reproducible from CMS and does not need to be redistributed.

Source: https://data.cms.gov/provider-data/dataset/9n3s-kdb3

CMS may rotate the file's direct download URL or change its schema. If a download or schema check fails, use the dataset page to retrieve the latest CSV and update `DATA_URL` / the column map in `src/pipeline.py`. Record the release and download date in your analysis.
