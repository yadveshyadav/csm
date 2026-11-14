# Tableau build notes

Tableau Public does not connect directly to PostgreSQL. Export `hrrp_hospital_measure` from `psql` to `data/hrrp_clean.csv`, then choose **Text file** in Tableau Public and open that CSV. The CSV contains public CMS data and is excluded from Git. If using a Tableau Desktop edition with a PostgreSQL connector, connect to `localhost:5432`, database `CSRM`, and table `hrrp_hospital_measure`; never save a real password in the workbook or repository.

## Worksheets

1. **Summary cards:** distinct hospitals, measure count, reporting period (`MIN(start_date)` to `MAX(end_date)`).
2. **Condition comparison:** `measure_name` vs median `excess_ratio`; reference line at 1.0.
3. **State view:** state vs median excess ratio, with hospital count in tooltip. Use the two-letter state field and set its geographic role.
4. **Hospital detail:** facility name/ID, state, measure, discharges, predicted rate, expected rate, excess ratio, dates.
5. **Volume context:** discharges by excess-ratio distribution, colored by measure. Avoid presenting a raw league table as a quality ranking.

## Dashboard

Place cards across the top, comparison and state charts in the middle, and a searchable detail table below. Add filters for measure, state, and reporting period. Include this definition in a text tile: **Excess readmission ratio = predicted readmissions divided by expected readmissions; values above 1 indicate more predicted readmissions than expected for the measure. CMS calculates expected rates using similar patients.**

When complete, publish to Tableau Public and add the public URL to the root README. Open the link in a logged-out/private browser window to confirm recruiter access.
