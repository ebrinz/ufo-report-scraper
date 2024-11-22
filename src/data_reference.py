import psycopg2
import psycopg2.extras
from db.connection import get_connection
from logger_config import get_logger
import pandas as pd
import re
from difflib import get_close_matches

logger = get_logger(__name__)

def generate_and_insert_reference_data():
    seed_geography_table()

def get_city_county_lat_lon_dataframe():
    file_path = "data/reference/citylatlon.txt"
    df = pd.read_csv(file_path, sep='\t')
    filtered_df = df[
        ~df['city_state'].str.contains(r"^\(blank\)|Grand Total", na=False)
    ]
    print(filtered_df.columns)
    print(filtered_df.head)
    return filtered_df

def seed_geography_table():
    geos = get_city_county_lat_lon_dataframe()
    values_to_insert = []
    insert_query = """
        INSERT INTO geography_lookup (report_id, city, state, county, latitude, longitude)
        VALUES %s
    """
    dbconn = get_connection()
    cursor = dbconn.cursor()
    cursor.execute("SELECT report_id, location from ufo_reports_transform;")
    rows = cursor.fetchall()
    values_to_insert = []
    for row in rows:
        report_id, location = row
        try:
            split_loc = location.split(',')
            if len(split_loc) < 2:
                logger.warning(f"Invalid location format for report_id {report_id}: {location}")
                continue
            city, state = split_loc[0].strip(), split_loc[1].strip()
            city, state = normalize_location(city, state)
            match = find_best_match(geos, city, state)
            if match is not None:
                values_to_insert.append((
                    report_id,
                    match['City'],
                    match['Row Labels'],
                    match['County'],
                    match['Latitude'],
                    match['Longitude']
                ))
            else:
                logger.warning(f"No match found for location: {location}")
        except Exception as e:
            logger.error(f"Error processing report {report_id}: {e}")
    if values_to_insert:
        try:
            with dbconn.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor,
                    insert_query,
                    values_to_insert
                )
            dbconn.commit()
            logger.info(f"Inserted {len(values_to_insert)} records into the geography table.")
        except Exception as e:
            logger.error(f"Error inserting into geography table: {e}")
            dbconn.rollback()
    else:
        logger.warning("No valid records to insert into the geography table.")

def normalize_location(city, state):
    city = re.sub(r"[^\w\s]", "", city).strip().upper()
    state = state.strip().upper()
    return city, state

def find_best_match(geos, city, state):
    geos['normalized_city'] = geos['City'].str.replace(r"[^\w\s]", "", regex=True).str.strip().str.upper()
    geos['normalized_state'] = geos['Row Labels'].str.strip().str.upper()
    match = geos[
        (geos['normalized_city'] == city) &
        (geos['normalized_state'] == state)
    ]
    if not match.empty:
        return match.iloc[0]
    city_matches = get_close_matches(city, geos['normalized_city'], n=1, cutoff=0.8)
    if city_matches:
        fuzzy_city = city_matches[0]
        fuzzy_match = geos[
            (geos['normalized_city'] == fuzzy_city) &
            (geos['normalized_state'] == state)
        ]
        if not fuzzy_match.empty:
            return fuzzy_match.iloc[0]
    return None

