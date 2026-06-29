import pandas as pd
import os
import logging

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

COLUMN_MAPS = {
    'yellow': {
        'tpep_pickup_datetime': 'pickup_datetime',
        'tpep_dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id',
    },
    'green': {
        'lpep_pickup_datetime': 'pickup_datetime',
        'lpep_dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id',
    },
    'fhv': {
        'pickup_datetime': 'pickup_datetime',
        'dropOff_datetime': 'dropoff_datetime',
        'PUlocationID': 'pickup_zone_id',
        'DOlocationID': 'dropoff_zone_id',
    },
    'fhvhv': {
        'pickup_datetime': 'pickup_datetime',
        'dropoff_datetime': 'dropoff_datetime',
        'PULocationID': 'pickup_zone_id',
        'DOLocationID': 'dropoff_zone_id',
    }
}

def detect_service(filename):
    if filename.startswith('fhvhv'):
        return 'fhvhv'
    elif filename.startswith('fhv'):
        return 'fhv'
    elif filename.startswith('green'):
        return 'green'
    elif filename.startswith('yellow'):
        return 'yellow'
    return None

def clean_file(filepath):
    filename = os.path.basename(filepath)
    service = detect_service(filename)

    if not service:
        logger.warning(f"Unknown service for file: {filename}")
        return

    logger.info(f"Cleaning: {filename}")

    df = pd.read_parquet(filepath)

    col_map = COLUMN_MAPS[service]
    df = df.rename(columns=col_map)

    df['service_type'] = service

    keep_cols = ['pickup_datetime', 'dropoff_datetime', 'pickup_zone_id',
                 'dropoff_zone_id', 'service_type']

    for col in ['fare_amount', 'tip_amount', 'tolls_amount', 'total_amount',
                'trip_distance', 'payment_type', 'passenger_count',
                'congestion_surcharge']:
        if col in df.columns:
            keep_cols.append(col)

    df = df[[c for c in keep_cols if c in df.columns]].copy()

    for col in ['fare_amount', 'tip_amount', 'tolls_amount', 'total_amount',
                'trip_distance', 'payment_type', 'passenger_count',
                'congestion_surcharge']:
        if col not in df.columns:
            df[col] = None

    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')

    before = len(df)
    df.drop_duplicates(inplace=True)
    logger.info(f"Removed {before - len(df)} duplicate rows")

    df['trip_duration_min'] = (
        df['dropoff_datetime'] - df['pickup_datetime']
    ).dt.total_seconds() / 60

    df['speed_mph'] = (
        df['trip_distance'] / df['trip_duration_min'].replace(0, None)
    ) * 60

    df['fare_per_mile'] = df['fare_amount'] / df['trip_distance'].replace(0, None)
    df['fare_per_minute'] = df['fare_amount'] / df['trip_duration_min'].replace(0, None)
    df['tip_pct'] = df['tip_amount'] / df['fare_amount'].replace(0, None) * 100
    df['is_airport_trip'] = (
        df['pickup_zone_id'].isin([1, 132, 138]) |
        df['dropoff_zone_id'].isin([1, 132, 138])
    ).astype(int)

    
    df['is_dirty'] = 0
    df['dirty_reason'] = None

    
    mask = df['pickup_datetime'].isna() | df['dropoff_datetime'].isna()
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'null_datetime'

    
    mask = df['fare_amount'].notna() & (df['fare_amount'] < 0)
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'negative_fare'

    
    mask = df['trip_distance'].notna() & df['fare_amount'].notna() & \
           (df['trip_distance'] == 0) & (df['fare_amount'] > 0)
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'zero_distance_nonzero_fare'

    
    mask = df['passenger_count'].notna() & (df['passenger_count'] == 0)
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'zero_passenger_count'

    
    mask = df['dropoff_datetime'] < df['pickup_datetime']
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'dropoff_before_pickup'

    
    mask = df['trip_duration_min'] > 300
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'duration_over_5hrs'

    
    mask = df['speed_mph'].notna() & (df['speed_mph'] > 120)
    df.loc[mask, 'is_dirty'] = 1
    df.loc[mask, 'dirty_reason'] = 'speed_over_120mph'

    
    df['congestion_surcharge'] = df['congestion_surcharge'].fillna(0)

    
    os.makedirs('cleaned', exist_ok=True)
    output_filename = filename.replace('.parquet', '.csv')
    output_path = os.path.join('cleaned', output_filename)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_filename} ({len(df)} rows)")


raw_files = sorted([
    os.path.join('raw', f) for f in os.listdir('raw') if f.endswith('.parquet')
])

logger.info(f"Found {len(raw_files)} files to clean")

for filepath in raw_files:
    clean_file(filepath)

logger.info("All files cleaned.")