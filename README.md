1. NYC Taxi Trip Pipeline



End to End Data Engineering and Analysis Pipeline for NYC TLC Taxi Trip data (2024).



2. Project Overview



Built a re-runnable data pipeline that ingests New York City taxi trip data Month over Month, stores it in a robust warehouse adjacent system, and powers an Interactive Dashboard which 

answers real question about Demand, Pricing/Tipping, service quality etc.



3. Technical Stack

* Python (ingestion + cleaning)
* DuckDB (Local Data Warehouse)
* SQL (Star Schema Modelling)
* Jupyter Notebook (Analysis)
* Power BI (Dashboard)



4. Data Source



NYC Taxi \ Limousine Commission (TLC) Trip Record Data



* URL: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* Services: Yellow Taxi, Green Taxi
* Period: January 2024 — December 2024
* Format: Apache Parquet
* Volume: \~41.8 million rows





5. Data Quality and assumptions



i) Column Standardizations



* "tpep\_pickup\_datetime" (yellow)/ "lpep\_pickup\_datetime" (green) = "pickup\_datetime"
* "tpep\_dropoff\_datetime" (yellow)/ "lpep\_dropoff\_datetime" (green) = "dropoff\_datetime"
* "PULocationID" = "pickup\_zone\_id"
* "DOLocationID" = "dropoff\_zone\_id"
* "Congestion Surcharge" = a derived column only present in the newer files, for files where there is no congestion surcharge, it is marked with 0.



ii) Duplicate Handling



&#x20;  Exact duplicate rows; all columns are identical; were removed during the cleaning step using pandas.DataFrame.drop\_duplicates(). 

&#x20;  The number of duplicates removed was logged before removal for each file.



iii) Dirty Row Flagging



* Dirty Rows are never deleted, they are only flagged. Flagging is done by doing "is\_dirty = 1", non dirty rows are flagged by "is\_dirty = 0".
* "is\_dirty = 1" rows are not considered during analysis, they are filtered by including "WHERE is\_dirty = 0" in the query.
* Each Dirty row are also paired with a "dirty\_reason". The reasons are several like:-
* "negative\_fare": Negative Fares are physically impossible.
* "zero\_distance\_nonzero\_fare": Cannot charge a trip for 0 distance.
* "zero\_passenger\_count": Every trip must have atleast 1 passenger.
* "dropoff\_before\_pickup": Dropping off a passenger before picking them up is impossible.
* "duration\_over\_5hrs": implausible duration.
* "speed\_over\_120mph": No NYC taxi travels at 120mph. 
* "null\_datetime": Cannot analyse a trip without a pickup time.



iv) Payment Type Assumption

&#x20;  

&#x20;  Payment Codes are defined by TLC:-

* 1 = Credit Card
* 2 = Cash
* 3 = No Charge
* 4 = Dispute
* 5 = Unknown
* 6 = Voided Trips



Payment codes outside of 1-6 are set to NULL



v) Geographic Assumptions



* Since mid-2016, NYC TLC data contains no latitude/longitude coordinates, All location data is zone-based using TLC taxi zones (1-265).
* Zone details like Name, Boroughs, Service type etc would come from official TLC Taxi data lookup table CSV. This data was joined by making a dimension table "dim\_zone".
* Airport zone IDs used: JFK = 132, LaGuardia = 138, EWR = 1.



vi) Tip Analysis Limitations

* tip\_amount is only populated for card payments (payment\_type = 1). 
* All cash trips have tip\_amount = 0 by default, this does not mean cash passengers did not tip, only that tips were not recorded digitally.
* Thus, Average tip % for card payments = 25.06%
* Average tip % including cash would be significantly lower due to forced zeros on all cash trips (misleading)





6. How to Run



Step 1 — Install dependencies



"pip install requests pyarrow pandas duckdb matplotlib jupyter"





Step 2 — Download raw Parquet files



"python download.py"



Step 3 — Clean and standardize data



"python clean.py"



Step 4 — Open Jupyter and run the notebook



"jupyter notebook"



Step 5 — Open "analysis/Duckdb\_pipeline.ipynb" and run all cells



This builds the star schema and runs all 5 analysis themes.





7. Star Schema



i) Fact\_trips (one row per trip)
* date\_key -> dim\_date  (year, month, day, hour, day\_name, is\_weekend)
* pickup\_zone\_key -> dim\_zone  (zone\_name, borough, service\_zone)
* dropoff\_zone\_key -> dim\_zone
* payment\_key -> dim\_payment (payment\_desc)



ii) Derived measures added in "Fact\_trips":-

* "trip\_duration\_min": dropoff time minus pickup time in minutes
* "speed\_mph": distance divided by duration multiplied by 60
* "fare\_per\_mile": fare divided by distance
* "fare\_per\_minute": fare divided by duration
* "tip\_pct": tip divided by fare multiplied by 100
* "is\_airport\_trip": 1 if pickup or dropoff is JFK, LGA, or EWR





8. Key Findings



* 39.9 million clean trips found across Green and Yellow taxi services in 2024.
* 6PM is viewed as the Peak hour with \~3 Million trips completed across the whole year of 2024; which is more than 12 times the hour than lowest trips.
* Thursday is found to be the busiest day of the week with \~6.2 Million Trips across 2024.
* October is found to be the Busiest Month with \~3.7 Million trips.
* JFK Airport, in Queens, is the Top Pickup Spot with \~1.8 Million pickups, more than any Manhattan Zone.
* 8 out of the top 10 pickup zones are in Manhattan.
* Average fare per mile is $13.66 across all clean trips across 2024.
* Credit card users tip an average of 25.06%, highest among all the other payment methods. Cash tip amounts are recorded as $0 by default and excluded from tip analysis.
* 4.57% of all records are dirty, meaning raw data collected which had quality issues; errors, anomalies, impossible values etc. Most common reason is `negative\_fare` (732,850 records).
* Dirty rows are not deleted, rather they are flagged with `is\_dirty = 1` and a `dirty\_reason` for full transparency.

