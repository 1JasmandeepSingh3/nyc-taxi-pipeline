CREATE TABLE dim_zone (
zone_id INT PRIMARY KEY,
zone_name VARCHAR(100),
borough VARCHAR(50),
service_zone VARCHAR(50)
);
INSERT INTO dim_zone (zone_id, zone_name, borough, service_zone)
SELECT LocationID, Zone, Borough, service_zone
FROM taxi_zone_lookup;
