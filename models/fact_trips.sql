CREATE TABLE fact_trips (
    trip_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date_key INT,
    pickup_zone_key INT,
    dropoff_zone_key INT,
    payment_key INT,
    service_type VARCHAR(10),
    fare_amount FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    total_amount FLOAT,
    trip_distance FLOAT,
    passenger_count FLOAT,
    congestion_surcharge FLOAT,
    trip_duration_min FLOAT,
    speed_mph FLOAT,
    fare_per_mile FLOAT,
    fare_per_minute FLOAT,
    tip_pct FLOAT,
    is_airport_trip TINYINT,
    is_dirty TINYINT,
    dirty_reason VARCHAR(50),
    
    FOREIGN KEY (date_key) 
    REFERENCES dim_date(date_key),
    
    FOREIGN KEY (pickup_zone_key)
    REFERENCES dim_zone(zone_id),
    
    FOREIGN KEY (dropoff_zone_key) 
    REFERENCES dim_zone(zone_id),
    
    FOREIGN KEY (payment_key)      
    REFERENCES dim_payment(payment_key)
);

INSERT INTO fact_trips (
date_key, pickup_zone_key, dropoff_zone_key, payment_key,
service_type, fare_amount, tip_amount, tolls_amount, total_amount,
trip_distance, passenger_count, congestion_surcharge,
trip_duration_min, speed_mph, fare_per_mile, fare_per_minute,
tip_pct, is_airport_trip, is_dirty, dirty_reason
)
SELECT DATE_FORMAT(r.pickup_datetime, '%Y%m%d%H') AS date_key,
r.pickup_zone_id AS pickup_zone_key,
r.dropoff_zone_id AS dropoff_zone_key,
CASE 
	WHEN r.payment_type IN (1,2,3,4,5,6) THEN r.payment_type 
	ELSE NULL 
END AS payment_key,
r.service_type,
r.fare_amount,
r.tip_amount,
r.tolls_amount,
r.total_amount,
r.trip_distance,
r.passenger_count,
r.congestion_surcharge,
r.trip_duration_min,
r.speed_mph,
r.fare_per_mile,
r.fare_per_minute,
r.tip_pct,
r.is_airport_trip,
r.is_dirty,
r.dirty_reason
FROM raw_trips r
WHERE r.pickup_datetime IS NOT NULL;