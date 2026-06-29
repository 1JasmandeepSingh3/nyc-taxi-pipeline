import requests
import os
import logging

# Setup logging
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


BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

def download_file(service, year, month):
    os.makedirs('raw', exist_ok=True)
    month_str = str(month).zfill(2)
    filename = f"{service}_tripdata_{year}-{month_str}.parquet"
    url = f"{BASE_URL}/{filename}"
    output_path = os.path.join('raw', filename)

    if os.path.exists(output_path):
        logger.info(f"Already exists, skipping: {filename}")
        return

    logger.info(f"Downloading: {filename}")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"Saved: {filename} ({size_mb:.1f} MB)")
    except Exception as e:
        logger.error(f"Failed: {filename} — {e}")



SERVICES = ['yellow', 'green', 'fhv', 'fhvhv']
START_YEAR, START_MONTH = 2024, 1
END_YEAR, END_MONTH = 2024, 12

for SERVICE in SERVICES:
    logger.info(f"--- Starting download for: {SERVICE} ---")
    year, month = START_YEAR, START_MONTH
    while (year, month) <= (END_YEAR, END_MONTH):
        download_file(SERVICE, year, month)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

logger.info("All downloads complete.")