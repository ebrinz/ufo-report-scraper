import pandas as pd
import requests
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_solar_data():
    Path("data").mkdir(exist_ok=True)

    url = "https://www.sidc.be/SILSO/DATA/SN_d_tot_V2.0.txt"

    logger.info("Fetching solar data from SILSO...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        logger.info("Processing data...")
        data = []
        lines = response.text.strip().split('\n')
        total_lines = len(lines)

        for i, line in enumerate(lines, 1):
            if i % 1000 == 0:
                logger.info(f"Processing line {i}/{total_lines}")

            try:
                parts = line.split()
                if len(parts) >= 4:
                    year, month, day, ssn = parts[:4]
                    data.append({
                        'date': f"{year}-{month.zfill(2)}-{day.zfill(2)}",
                        'sunspot_number': float(ssn)
                    })
            except ValueError as e:
                logger.error(f"Error processing line {i}: {e}")
                continue

        logger.info("Creating DataFrame...")
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['solar_flares'] = df['sunspot_number'] * 0.1

        output_path = "data/solar_activity.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Solar data saved to {output_path}")
        logger.info(f"Total records: {len(df)}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    fetch_solar_data()
