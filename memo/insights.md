# CMS Hospital Readmissions: Client Insight Memo

**To:** Hospital quality leadership | **From:** Analytics project team | **Subject:** Prioritizing review of 30-day readmission measures
**CMS reporting period:** July 1, 2021–June 30, 2024

## Question and scope

Which hospital-condition measures show higher-than-expected readmissions, and how should leaders prioritize follow-up? This analysis summarizes 18,330 CMS HRRP hospital-condition records across 3,055 hospitals and six measures. The CMS excess readmission ratio compares predicted readmissions with expected readmissions for similar patients.

## Findings

1. **Measure medians cluster near 1.0.** Median excess ratios range from 0.9916 for hip/knee replacement to 1.0000 for coronary artery bypass graft (CABG; unrounded 0.99995). At the measure level, the dataset does not show a large separation in typical hospital ratios.
2. **Roughly half of available hospital-measure ratios exceed 1.0.** The share ranges from 46.8% for pneumonia to 49.9% for CABG. This is a descriptive count of reported ratios, not a patient-level readmission probability or a ranking of hospital quality.
3. **Discharge volume is associated with lower ratios in the complete-case regression, but the model explains little overall variation.** Among 8,037 records with both ratio and discharge volume available, the volume coefficient is -0.0000396 per discharge (HC3 robust p < 0.001); R-squared is 0.024. The association may reflect aggregation, reporting, or other unmeasured factors and is not causal.

## Recommendation

Use the measure-level and volume patterns to choose a condition for a focused operational review. Before changing a care pathway, validate facility-level cases against local discharge-transition and follow-up processes. Avoid using a single aggregate ratio as a stand-alone hospital score.

## Limitations

CMS aggregate measures cannot identify why a patient returned to hospital. 6,610 of 18,330 rows have no excess ratio; the regression further excludes rows without discharge volume. The model is descriptive and is not a new patient-level case-mix adjustment. Smaller denominators can make facility-level comparisons less stable.
