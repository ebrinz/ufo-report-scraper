from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_report_datetime(report_date: Optional[str]) -> Optional[datetime]:
    if not report_date:
        return None
    try:
        # Handle various time formats
        if "AM" in report_date or "PM" in report_date:
            try:
                # Try full format first
                return datetime.strptime(report_date, "%m/%d/%Y %I:%M:%S %p")
            except:
                # Try without seconds
                return datetime.strptime(report_date, "%m/%d/%Y %I:%M %p")
        elif "/" in report_date:
            parts = report_date.split()
            if len(parts) > 1:
                return datetime.strptime(f"{parts[0]} {parts[1]}", "%m/%d/%Y %H:%M")
            else:
                return datetime.strptime(parts[0], "%m/%d/%Y")
    except Exception as e:
        logger.debug(f"Failed to parse date: {report_date} - {str(e)}")
        return None

def analyze_peak_times(df: pd.DataFrame):
    # Night hours (8 PM - 4 AM)
    night_hours = [20, 21, 22, 23, 0, 1, 2, 3, 4]
    night_sightings = df[df['date'].dt.hour.isin(night_hours)]

    print("\nNight vs Day Analysis:")
    total = len(df)
    night_count = len(night_sightings)
    day_count = total - night_count
    print(f"Night sightings (8 PM - 4 AM): {night_count:,} ({night_count/total*100:.1f}%)")
    print(f"Day sightings (4 AM - 8 PM): {day_count:,} ({day_count/total*100:.1f}%)")

    # Peak time analysis
    df['time_of_day'] = pd.cut(df['date'].dt.hour,
                              bins=[-1, 4, 8, 12, 16, 20, 24],
                              labels=['Late Night', 'Early Morning', 'Morning',
                                    'Afternoon', 'Evening', 'Night'])

    time_dist = df.groupby('time_of_day').size()
    print("\nTime of Day Distribution:")
    for time, count in time_dist.items():
        print(f"{time:13s} - {count:5d} sightings ({count/total*100:.1f}%)")

def analyze_shapes_by_time(df: pd.DataFrame):
    # Most common shapes during different times
    df['time_period'] = pd.cut(df['date'].dt.hour,
                              bins=[-1, 4, 12, 20, 24],
                              labels=['Night (12-4)', 'Morning (4-12)',
                                    'Evening (12-8)', 'Night (8-12)'])

    shape_time = pd.crosstab(df['shape'], df['time_period'])

    print("\nTop Shapes by Time Period:")
    for period in shape_time.columns:
        print(f"\n{period}:")
        top_shapes = shape_time[period].nlargest(5)
        for shape, count in top_shapes.items():
            if count > 0:
                print(f"{shape:10s} - {count:4d} sightings")

def analyze_temporal_patterns():
    reports = []
    for json_file in Path("data/raw/raw_month_data").glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                reports.extend(data)
        except Exception as e:
            logger.error(f"Error reading {json_file}: {e}")

    logger.info(f"Loaded {len(reports)} reports")

    df = pd.DataFrame(reports)
    df['date'] = df['reported'].apply(parse_report_datetime)
    df = df.dropna(subset=['date'])

    print(f"\nAnalyzing {len(df):,} reports with valid timestamps")

    analyze_peak_times(df)
    analyze_shapes_by_time(df)

    return df

if __name__ == "__main__":
    try:
        df = analyze_temporal_patterns()

        # Additional insights
        print("\nMonthly Trends:")
        monthly = df.groupby(df['date'].dt.to_period('M')).size()
        peak_months = monthly.nlargest(5)
        print("\nPeak Months for Sightings:")
        for month, count in peak_months.items():
            print(f"{month} - {count:,} sightings")

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise
