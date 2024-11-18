from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
from typing import List, Optional, Dict, Generator
import logging
from collections import Counter
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UFOReport:
    report_id: Optional[str]
    entered: Optional[str]
    occurred: Optional[str]
    reported: Optional[str]
    posted: Optional[str]
    location: Optional[str]
    shape: Optional[str]
    duration: Optional[str]
    description: Optional[str]
    status_code: Optional[int]
    characteristics: Optional[str]

def parse_report(data: Dict) -> UFOReport:
    return UFOReport(
        report_id=data.get("report_id"),
        entered=data.get("entered"),
        occurred=data.get("occurred"),
        reported=data.get("reported"),
        posted=data.get("posted"),
        location=data.get("location"),
        shape=data.get("shape"),
        duration=data.get("duration"),
        description=data.get("description"),
        status_code=data.get("status_code"),
        characteristics=data.get("characteristics")
    )

def read_json_files(directory: str) -> Generator[List[UFOReport], None, None]:
    data_dir = Path(directory)

    if not data_dir.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")

    for json_file in data_dir.glob("*.json"):
        try:
            logger.info(f"Processing {json_file.name}")
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                reports = [parse_report(report) for report in data]
                yield reports
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding {json_file.name}: {e}")
        except Exception as e:
            logger.error(f"Error processing {json_file.name}: {e}")

def get_location_stats(reports: List[UFOReport]) -> Dict[str, int]:
    locations = Counter()
    for report in reports:
        if report.location:
            state = report.location.split(",")[-1].strip()
            if len(state) == 2:  # US state abbreviation
                locations[state] += 1
    return dict(locations.most_common(10))

def get_year_stats(reports: List[UFOReport]) -> Dict[str, int]:
    years = Counter()
    for report in reports:
        if report.posted:
            try:
                year = report.posted.split("/")[-1]
                years[year] += 1
            except:
                continue
    return dict(years.most_common(10))

def process_reports(directory: str = "raw_month_data") -> List[UFOReport]:
    all_reports = []
    total_files = 0
    total_reports = 0

    for reports in read_json_files(directory):
        total_files += 1
        total_reports += len(reports)
        all_reports.extend(reports)

    logger.info(f"Processed {total_files} files containing {total_reports} reports")
    return all_reports

if __name__ == "__main__":
    reports = process_reports()

    print("\nBasic Statistics:")
    print(f"Total reports: {len(reports)}")

    # Shape analysis
    shapes = Counter(report.shape for report in reports if report.shape)
    print("\nTop 10 Shapes:")
    for shape, count in shapes.most_common(10):
        print(f"{shape}: {count}")

    # Location analysis
    locations = get_location_stats(reports)
    print("\nTop 10 States:")
    for state, count in locations.items():
        print(f"{state}: {count}")

    # Year analysis
    years = get_year_stats(reports)
    print("\nTop 10 Years:")
    for year, count in years.items():
        print(f"{year}: {count}")

    # Characteristics analysis
    characteristics = Counter()
    for report in reports:
        if report.characteristics:
            for char in report.characteristics.split(","):
                characteristics[char.strip()] += 1

    print("\nTop 10 Characteristics:")
    for char, count in characteristics.most_common(10):
        print(f"{char}: {count}")