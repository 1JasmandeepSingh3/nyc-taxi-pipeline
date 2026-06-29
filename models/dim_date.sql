INSERT INTO dim_date (date_key, full_date, year, month, month_name, day, hour, day_of_week, day_name, is_weekend)
SELECT DISTINCT
    DATE_FORMAT(pickup_datetime, '%Y%m%d%H') AS date_key,
    DATE(pickup_datetime)                    AS full_date,
    YEAR(pickup_datetime)                    AS year,
    MONTH(pickup_datetime)                   AS month,
    MONTHNAME(pickup_datetime)               AS month_name,
    DAY(pickup_datetime)                     AS day,
    HOUR(pickup_datetime)                    AS hour,
    DAYOFWEEK(pickup_datetime)               AS day_of_week,
    DAYNAME(pickup_datetime)                 AS day_name,
    IF(DAYOFWEEK(pickup_datetime) IN (1,7), 1, 0) AS is_weekend
FROM raw_trips
WHERE pickup_datetime IS NOT NULL;