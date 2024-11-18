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
            # Format: "1/20/2007 11:45:34 AM"
            return datetime.strptime(report_date.split()[0] + " " + report_date.split()[1],
                                   "%m/%d/%Y %H:%M")
        elif "/" in report_date:
            # Format: "1/5/2000 07:44"
            parts = report_date.split()
            if len(parts) > 1:
                return datetime.strptime(f"{parts[0]} {parts[1]}", "%m/%d/%Y %H:%M")
            else:
                return datetime.strptime(parts[0], "%m/%d/%Y")
    except:
        return None
    return None

def analyze_temporal_patterns(df: pd.DataFrame):
    # Hourly analysis
    df['hour'] = df['date'].dt.hour
    hourly_pattern = df.groupby('hour').size().sort_index()

    print("\nHourly Pattern (24-hour):")
    for hour, count in hourly_pattern.items():
        print(f"{hour:02d}:00 - {count:5d} sightings")

    # Peak hours
    peak_hours = hourly_pattern.nlargest(5)
    print("\nPeak Hours:")
    for hour, count in peak_hours.items():
        print(f"{hour:02d}:00 - {count:5d} sightings")

    # Season analysis with percentages
    df['season'] = pd.cut(df['date'].dt.month,
                         bins=[0,3,6,9,12],
                         labels=['Winter', 'Spring', 'Summer', 'Fall'])
    season_pattern = df.groupby('season').size()
    total = season_pattern.sum()

    print("\nSeasonal Pattern:")
    for season, count in season_pattern.items():
        percentage = (count / total) * 100
        print(f"{season:8s} - {count:6d} sightings ({percentage:.1f}%)")

    # Day of week with percentages
    df['day_of_week'] = df['date'].dt.day_name()
    dow_pattern = df.groupby('day_of_week').size()
    total_days = dow_pattern.sum()

    print("\nDay of Week Pattern:")
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days_order:
        count = dow_pattern[day]
        percentage = (count / total_days) * 100
        print(f"{day:9s} - {count:5d} sightings ({percentage:.1f}%)")

def analyze_shapes(df: pd.DataFrame):
    # Shape trends for recent years
    recent_years = sorted(df['year'].unique())[-5:]
    shape_counts = df[df['year'].isin(recent_years)].groupby(['year', 'shape']).size().unstack(fill_value=0)

    print("\nTop 5 Shapes by Recent Years:")
    for year in recent_years:
        top_shapes = shape_counts.loc[year].nlargest(5)
        print(f"\n{year}:")
        for shape, count in top_shapes.items():
            if count > 0:  # Only show non-zero counts
                print(f"{shape:10s} - {count:4d} sightings")

def analyze_correlation():
    reports = []
    for json_file in Path("raw_month_data").glob("*.json"):
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

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    print("\nBasic Statistics:")
    print(f"Total valid reports: {len(df):,}")
    print(f"Date range: {df['date'].min().year} to {df['date'].max().year}")
    print(f"Number of unique shapes: {df['shape'].nunique()}")
    print(f"Number of unique locations: {df['location'].nunique():,}")

    analyze_temporal_patterns(df)
    analyze_shapes(df)

    return df

if __name__ == "__main__":
    try:
        df = analyze_correlation()

        # Identify significant clusters
        df['date_only'] = df['date'].dt.date
        clusters = df.groupby('date_only').size()

        print("\nMajor Sighting Events (75+ reports):")
        major_events = clusters[clusters >= 75].sort_values(ascending=False)
        for date, count in major_events.items():
            print(f"{date} - {count:3d} sightings")

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise