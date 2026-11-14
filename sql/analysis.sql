-- Run after src/pipeline.py has loaded hrrp_hospital_measure.
SELECT COUNT(*) AS records,
       COUNT(DISTINCT facility_id) AS hospitals,
       COUNT(DISTINCT measure_name) AS measures
FROM hrrp_hospital_measure;

-- CMS marks some measure estimates as unavailable/suppressed. Keep them NULL.
SELECT measure_name,
       COUNT(*) AS records,
       COUNT(excess_ratio) AS records_with_ratio,
       ROUND(AVG(excess_ratio)::numeric, 4) AS mean_excess_ratio,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY excess_ratio)::numeric, 4) AS median_excess_ratio,
       ROUND(AVG((excess_ratio > 1)::int)::numeric, 4) AS share_above_1
FROM hrrp_hospital_measure
GROUP BY measure_name ORDER BY median_excess_ratio DESC;

-- Sample-size context: do not interpret small-volume extremes as stable rankings.
SELECT measure_name,
       CASE WHEN discharges IS NULL THEN 'Unknown'
            WHEN discharges < 100 THEN '<100'
            WHEN discharges < 300 THEN '100-299'
            ELSE '300+' END AS volume_band,
       COUNT(*) AS records,
       ROUND(AVG(excess_ratio)::numeric, 4) AS mean_excess_ratio
FROM hrrp_hospital_measure
WHERE excess_ratio IS NOT NULL
GROUP BY measure_name, volume_band
ORDER BY measure_name, volume_band;
