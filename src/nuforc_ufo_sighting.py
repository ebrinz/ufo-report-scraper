from typing import List, Union
import re
from urllib.parse import urlparse, urljoin
from ufo_sighting_field import UFOSightingField, SearchInstance
import requests

class NUFORCUFOSighting:
    BASE_URL = "https://nuforc.org"
    def __init__(self):
        field_definitions = [
            ("Sighting ID", "NUFORC UFO Sighting", SearchInstance.LAST),
            ("Occurred", "Occurred:", SearchInstance.FIRST),
            ("Reported", "Reported:", SearchInstance.FIRST),
            ("Duration", "Duration:", SearchInstance.FIRST),
            ("No of observers", "No of observers:", SearchInstance.FIRST),
            ("Location", "Location:", SearchInstance.FIRST),
            ("Location details", "Location details:", SearchInstance.FIRST),
            ("Shape", "Shape:", SearchInstance.FIRST),
            ("Color", "Color:", SearchInstance.FIRST),
            ("Estimated Size", "Estimated Size:", SearchInstance.FIRST),
            ("Viewed From", "Viewed From:", SearchInstance.FIRST),
            ("Direction from Viewer", "Direction from Viewer:", SearchInstance.FIRST),
            ("Angle of Elevation", "Angle of Elevation:", SearchInstance.FIRST),
            ("Closest Distance", "Closest Distance:", SearchInstance.FIRST),
            ("Estimated Speed", "Estimated Speed:", SearchInstance.FIRST),
            ("Explanation", "Explanation:", SearchInstance.FIRST),
            ("Characteristics", "Characteristics:", SearchInstance.FIRST),
            ("Description", "<br>", SearchInstance.FIRST),
            ("Media URLs", "<script", SearchInstance.FIRST),
            ("Posted", "Posted", SearchInstance.FIRST, "©")
        ]
        self.expected_fields = []
        previous_field = None
        for field_def in field_definitions:
            name, pattern, search_instance, *end_pattern = field_def
            field = UFOSightingField(
                name=name,
                start_pattern=pattern,
                start_pattern_search_instance=search_instance,
                end_pattern=end_pattern[0] if end_pattern else None
            )
            field.set_expected_after_field(previous_field)
            self.expected_fields.append(field)
            previous_field = field

    def scrape(self, url_or_id: Union[str, int]) -> None:
        sighting_id = re.search(r'id=(\d+)', str(url_or_id)).group(1) if '?' in str(url_or_id) else str(url_or_id)
        full_url = urljoin(self.BASE_URL, f"/sighting/?id={sighting_id}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(full_url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text
            for field in self.expected_fields:
                field.scrape(content)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {full_url}: {str(e)}")
            raise

if __name__ == "__main__":
    sighting = NUFORCUFOSighting()
    sighting.scrape(184251)
    for field in sighting.expected_fields:
        print(field)

