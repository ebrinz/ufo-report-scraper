from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import List, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_report_datetime(report_date: Optional[str]) -> Optional[datetime]:
    if not report_date:
        return None
    try:
        if "AM" in report_date or "PM" in report_date:
            try:
                return datetime.strptime(report_date, "%m/%d/%Y %I:%M:%S %p")
            except:
                return datetime.strptime(report_date, "%m/%d/%Y %I:%M %p")
        elif "/" in report_date:
            parts = report_date.split()
            if len(parts) > 1:
                return datetime.strptime(f"{parts[0]} {parts[1]}", "%m/%d/%Y %H:%M")
            else:
                return datetime.strptime(parts[0], "%m/%d/%Y")
    except:
        return None

def analyze_shape_characteristics(df: pd.DataFrame):
    # Clean up blank shapes
    df['shape'] = df['shape'].fillna('Unknown')
    df.loc[df['shape'] == '', 'shape'] = 'Unknown'

    # Analyze shapes by time of day
    df['hour_group'] = pd.cut(df['date'].dt.hour,
                             bins=[-1, 4, 8, 12, 16, 20, 24],
                             labels=['Late Night', 'Dawn', 'Morning',
                                   'Afternoon', 'Dusk', 'Night'])

    print("\nTop Shapes Overall:")
    shape_counts = df['shape'].value_counts()
    total_sightings = len(df)
    for shape, count in shape_counts.head(10).items():
        percentage = (count / total_sightings) * 100
        print(f"{shape:12s} - {count:5d} sightings ({percentage:5.1f}%)")

    # Duration analysis for each shape
    df['duration_clean'] = df['duration'].fillna('Unknown')
    duration_by_shape = pd.crosstab(df['shape'], df['duration_clean'])

    print("\nDuration Patterns for Top Shapes:")
    for shape in shape_counts.head(5).index:
        durations = duration_by_shape.loc[shape].nlargest(3)
        print(f"\n{shape}:")
        for duration, count in durations.items():
            if count > 0:
                print(f"  {duration:15s} - {count:4d} sightings")

def analyze_characteristics_patterns(df: pd.DataFrame):
    # Filter out rows with no characteristics
    df_with_chars = df[df['characteristics'].notna()]

    # Common characteristics to look for
    characteristics = {
        'Lights': 'light',
        'Sound': 'sound',
        'Hovering': 'hover',
        'Fast Moving': 'fast',
        'Color Change': 'color change',
        'Trail': 'trail',
        'Formation': 'formation',
        'Rotation': 'rotat',
        'Beam': 'beam',
        'Pulsating': 'pulsat'
    }

    print("\nCharacteristic Patterns:")
    total_with_chars = len(df_with_chars)

    for char_name, search_term in characteristics.items():
        count = df_with_chars['characteristics'].str.contains(
            search_term, case=False, na=False
        ).sum()
        if count > 0:
            percentage = (count / total_with_chars) * 100
            print(f"{char_name:12s} - {count:5d} reports ({percentage:5.1f}%)")

def analyze_shapes():
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

    analyze_shape_characteristics(df)
    analyze_characteristics_patterns(df)

    return df

if __name__ == "__main__":
    try:
        df = analyze_shapes()

        # Shape patterns by time period
        print("\nShape Distribution by Time Period:")
        df['time_period'] = pd.cut(df['date'].dt.hour,
                                 bins=[-1, 6, 12, 18, 24],
                                 labels=['Night', 'Morning', 'Afternoon', 'Evening'])

        time_shapes = pd.crosstab(df['time_period'], df['shape'])

        for period in ['Night', 'Morning', 'Afternoon', 'Evening']:
            print(f"\n{period} Top Shapes:")
            top_shapes = time_shapes.loc[period].nlargest(5)
            for shape, count in top_shapes.items():
                if count > 0:
                    percentage = (count / time_shapes.loc[period].sum()) * 100
                    print(f"{shape:12s} - {count:4d} sightings ({percentage:5.1f}%)")

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise
