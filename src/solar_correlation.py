from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import List, Optional
import logging
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_report_datetime(report_date: Optional[str]) -> Optional[datetime]:
    if not report_date:
        return None
    try:
        if "AM" in report_date or "PM" in report_date:
            return datetime.strptime(report_date.split()[0] + " " + report_date.split()[1],
                                   "%m/%d/%Y %H:%M")
        elif "/" in report_date:
            parts = report_date.split()
            if len(parts) > 1:
                return datetime.strptime(f"{parts[0]} {parts[1]}", "%m/%d/%Y %H:%M")
            else:
                return datetime.strptime(parts[0], "%m/%d/%Y")
    except:
        return None
    return None

def load_solar_data():
    try:
        solar_df = pd.read_csv("data/solar_activity.csv")
        solar_df["date"] = pd.to_datetime(solar_df["date"])
        return solar_df
    except Exception as e:
        logger.error(f"Error loading solar data: {e}")
        return None

def analyze_solar_correlation(ufo_df: pd.DataFrame, solar_df: pd.DataFrame):
    daily_sightings = ufo_df.groupby(ufo_df["date"].dt.date).size().reset_index()
    daily_sightings.columns = ["date", "sighting_count"]
    daily_sightings["date"] = pd.to_datetime(daily_sightings["date"])

    merged_df = pd.merge(daily_sightings, solar_df, on="date", how="inner")

    correlation_sunspots = stats.pearsonr(merged_df["sighting_count"],
                                        merged_df["sunspot_number"])
    correlation_flares = stats.pearsonr(merged_df["sighting_count"],
                                      merged_df["solar_flares"])

    print("\nSolar Activity Correlation Analysis:")
    print(f"Correlation with sunspot numbers: {correlation_sunspots[0]:.3f} (p={correlation_sunspots[1]:.3f})")
    print(f"Correlation with solar flares: {correlation_flares[0]:.3f} (p={correlation_flares[1]:.3f})")

    high_activity_days = merged_df[merged_df["solar_flares"] > merged_df["solar_flares"].quantile(0.95)]
    print("\nUFO Sightings during High Solar Activity:")
    print(f"Average sightings on normal days: {merged_df['sighting_count'].mean():.2f}")
    print(f"Average sightings during high solar activity: {high_activity_days['sighting_count'].mean():.2f}")

def analyze_correlation():
    reports = []
    for json_file in Path("raw_month_data").glob("*.json"):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                reports.extend(data)
        except Exception as e:
            logger.error(f"Error reading {json_file}: {e}")

    logger.info(f"Loaded {len(reports)} reports")

    df = pd.DataFrame(reports)
    df["date"] = df["reported"].apply(parse_report_datetime)
    df = df.dropna(subset=["date"])

    solar_df = load_solar_data()
    if solar_df is not None:
        analyze_solar_correlation(df, solar_df)
    else:
        logger.error("Could not perform solar correlation analysis due to missing solar data")

    return df

if __name__ == "__main__":
    try:
        df = analyze_correlation()
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise