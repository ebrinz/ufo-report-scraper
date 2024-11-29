import re
import csv
import time
import dateparser
import pandas as pd 

from db.queries import fetch_raw_reports, insert_report_transform, insert_reports_transform_bulk

import nltk
from nltk.tokenize import sent_tokenize


from logger_config import get_logger
logger = get_logger(__name__)

# us_geos_reorg = {}
# with open('data/reference/citylatlon.txt', mode='r') as f:
#     us_geos = csv.DictReader(f, delimiter='\t')
#     for item in us_geos:
#         if item['state'] not in us_geos_reorg:
#             us_geos_reorg[item['state']] = {}
#         if item['city'] not in us_geos_reorg[item['state']]:
#             us_geos_reorg[item['state']][item['city']] = {}
#         us_geos_reorg[item['state']][item['city']]['lat'] = item['latitude']
#         us_geos_reorg[item['state']][item['city']]['lon'] = item['longitude']
#     f.close()

# def get_city_county_lat_lon_dataframe():
#     file_path = "data/reference/citylatlon.txt"
#     df = pd.read_csv(file_path)
#     filtered_df = df[
#         ~df['city_state'].str.contains(r"^\(blank\)|Grand Total", na=False)
#     ]
#     return filtered_df

# def format_location(loc):
#     geos = get_city_county_lat_lon_dataframe
#     output = None
#     split_loc = loc.split(',')
#     city = split_loc[0].strip()
#     state = split_loc[1].strip()
#     city_split = re.findall(r'[\w\s.]+', city)
#     if len(city_split) > 0:
#         city = city_split[0].strip()
#     if state.upper() in us_geos_reorg and city.upper() in us_geos_reorg[state.upper()]:
#         output = [us_geos_reorg[state.upper()][city.upper()]['lat'], us_geos_reorg[state.upper()][city.upper()]['lon']]
#     else:
#         output = None
#     return output

def format_timestamp(ts):
    output = None
    try:
        dt = dateparser.parse(ts)
        if dt:
            # Convert datetime object to epoch time (seconds since 1970-01-01)
            output = int(time.mktime(dt.timetuple()))
    except Exception as e:
        print(f"Error parsing timestamp: {ts} -> {e}")
    return output

def format_shape(shape):
    upper_shape = str(shape).upper()
    return upper_shape

def format_duration(dur):
    """
    Parse the duration into seconds as accurately as possible. 
    Handle common duration formats such as '1-2 min', 'few seconds', '3:45' (HH:MM), etc.
    """
    if not dur:
        return None

    output = 0
    skip = False
    low_dur = str(dur).lower().strip()  # Ensure the duration is a string and strip extra spaces
    sub_dur = re.sub(r'[\'+~,]', '', low_dur)
    split_dur = re.findall(r'(\d+[.\d+]*[\s]*[-to]*[\s]*[.\d+]*|[a-z]+)', sub_dur)
    cleaned_list = []

    # Check if the format is in HH:MM:SS
    if ':' in dur:
        multiplyer = 1
        hhmmss = re.findall(r'\d+:\d+[:\d+]?', dur)
        if hhmmss:
            split_ssmmhh = hhmmss[0].split(':')
            split_ssmmhh.reverse()
            for idx, i in enumerate(split_ssmmhh):
                if i.isdigit():  # Check if valid digits are present
                    output = output + int(i) * multiplyer
                    multiplyer *= 60
            return output

    # Parse the non-HH:MM:SS formats
    for idx, i in enumerate(split_dur):
        if i in ['a', 'an']:
            cleaned_list.append(1)
        elif i in ['few']:
            cleaned_list.append(5)
        elif re.match(r'\d+[.\d+]*[\s]*[-to]*[\s]*\d+[.\d+]*', i):
            split_element = re.findall(r'\d+', i)
            try:
                cleaned_list.append((float(split_element[0]) + float(split_element[1])) / 2)
            except:
                cleaned_list.append(split_element[0].strip())
        elif i not in ['approx', 'aprox', 'about', 'over', 'under', 'less', 'more', 'than']:
            cleaned_list.append(i.strip())

    try:
        for jdx, j in enumerate(cleaned_list):
            if jdx == len(cleaned_list) - 1:
                break
            try:
                temp_num = float(cleaned_list[jdx])
                prefix = ''.join([*cleaned_list[jdx + 1]][0:3])
                if prefix in ['sec', 's']:
                    output = output + temp_num * 1
                elif prefix in ['min', 'mns', 'mn', 'm']:
                    output = output + temp_num * 60
                elif prefix in ['hou', 'hrs', 'hr', 'h']:
                    output = output + temp_num * 3600
                elif prefix in ['day']:
                    output = output + temp_num * 86400
                else:
                    skip = True
            except (ValueError, IndexError):
                continue
    except Exception as e:
        skip = True

    output = int(output)
    if skip or output == 0:
        output = None  # Return None if unable to parse the duration properly
    return output

def clean_descriptions (text):
    text = re.sub(r'\(\(.*?\)\)', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    text = text.strip()
    sentences = sent_tokenize(text)
    return sentences


# transform the raw report into a little bit better shape
# will transfomr geo in another step
# embeddings also in another step

def transform_report(raw_report):
    try:
        transformed_report = {
            "report_id": raw_report["report_id"],
            "entered": format_timestamp(raw_report["entered"]) if raw_report["entered"] else None,
            "occurred": format_timestamp(raw_report["occurred"]) if raw_report["occurred"] else None,
            "reported": format_timestamp(raw_report["reported"]) if raw_report["reported"] else None,
            "posted": format_timestamp(raw_report["posted"]) if raw_report["posted"] else None,
            "location": raw_report["location"].upper() if raw_report["location"] else None,
            "shape": format_shape(raw_report["shape"]) if raw_report["shape"] else None,
            "duration": format_duration(raw_report["duration"]) if raw_report["duration"] else None,
            "description": clean_descriptions(raw_report["description"]) if raw_report["description"] else None,
        }
        return transformed_report
    except Exception as e:
        logger.error(f"Error transforming report: {raw_report.get('report_id', 'Unknown')}, error: {e}")
        return None


def process_and_insert_transformed_reports():
    raw_reports = fetch_raw_reports()
    nltk.download('punkt')
    transformed_reports = [transform_report(report) for report in raw_reports if report]
    valid_reports = [report for report in transformed_reports if report]
    if valid_reports:
        try:
            insert_reports_transform_bulk(valid_reports)
            logger.info(f"Successfully inserted {len(valid_reports)} transformed reports.")
        except Exception as e:
            logger.error(f"Error during bulk insert: {e}")
    else:
        logger.warning("No valid transformed reports to insert.")


