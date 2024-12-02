from typing import Optional, List
from enum import Enum, auto
import re

class SearchInstance(Enum):
    FIRST = auto()
    LAST = auto()

class UFOSightingField:
    def __init__(
        self,
        name: str,
        start_pattern: str = "",
        start_pattern_search_instance: SearchInstance = SearchInstance.FIRST,
        end_pattern: Optional[str] = None,
        expected_after_field: Optional['UFOSightingField'] = None,
        expected_before_field: Optional['UFOSightingField'] = None
    ):
        self.set_name(name)
        self.set_start_pattern(start_pattern)
        self.set_start_pattern_search_instance(start_pattern_search_instance)
        self.set_start_extraction_position(0)
        self.set_end_pattern(end_pattern)
        self.set_end_extraction_position(-1)
        self.set_expected_before_field(expected_before_field)
        self.set_expected_after_field(expected_after_field)
        self._extracted_values: List[str] = []

    def __str__(self) -> str:
        return (
            f"{self.name()}:\n"
            f"    Start Pattern: {self.start_pattern()}\n"
            f"    Search Instance: {self.start_pattern_search_instance()}\n"
            f"    Start Extraction Position: {self.start_extraction_position()}\n"
            f"    End Pattern: {self.end_pattern()}\n"
            f"    End Extraction Position: {self.end_extraction_position()}\n"
            f"    Expected After: {self.expected_after_field().name() if self.expected_after_field() else 'None'}\n"
            f"    Expected Before: {self.expected_before_field().name() if self.expected_before_field() else 'None'}\n"
            f"    Extracted Values: {self.extracted_values()}"
        )

    def name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        self._name = name

    def start_pattern(self) -> str:
        return self._start_pattern

    def set_start_pattern(self, pattern: str) -> None:
        self._start_pattern = pattern

    def start_pattern_search_instance(self) -> SearchInstance:
        return self._start_pattern_search_instance

    def set_start_pattern_search_instance(self, instance: SearchInstance) -> None:
        self._start_pattern_search_instance = instance

    def start_extraction_position(self) -> int:
        return self._start_extraction_position

    def set_start_extraction_position(self, position: int) -> None:
        self._start_extraction_position = position

    def end_pattern(self) -> Optional[str]:
        return self._end_pattern

    def set_end_pattern(self, pattern: str) -> None:
        self._end_pattern = pattern

    def end_extraction_position(self) -> int:
        return self._end_extraction_position

    def set_end_extraction_position(self, position: int) -> None:
        self._end_extraction_position = position

    def expected_after_field(self) -> Optional['UFOSightingField']:
        if self._expected_after_field is None: self.set_expected_after_field(self.__class__(name="No Field Expected Here"))
        return self._expected_after_field

    def set_expected_after_field(self, field: Optional['UFOSightingField']) -> None:
        self._expected_after_field = field
        if field is not None:
            field.set_expected_before_field(self)
            if not field.end_pattern(): field.set_end_pattern(self.start_pattern())

    def expected_before_field(self) -> Optional['UFOSightingField']:
        return self._expected_before_field

    def set_expected_before_field(self, field: Optional['UFOSightingField']) -> None:
        self._expected_before_field = field

    def extracted_values(self) -> List[str]:
        return self._extracted_values

    def set_extracted_values(self, raw_text: str) -> None:
        self._extracted_values = re.sub(r'<[^>]*>|<.*$|[ \t]+', lambda m: ' ' if m.group().isspace() else '', raw_text).strip()

    def start_pattern_len(self) -> int:
        return len(self.start_pattern()) if self.start_pattern() else 0
    
    def expected_after_field_end_extraction_position(self) -> int:
        return self.expected_after_field().end_extraction_position()

    def find_start_pattern_position(self, content: str) -> int:
        if self.start_pattern_search_instance() == SearchInstance.LAST:
            return content.rfind(self.start_pattern())
        else:
            return content.find(self.start_pattern(), self.expected_after_field_end_extraction_position() + 1)

    def scrape(self, content: str) -> None:
        self.set_start_extraction_position(self.start_pattern_len() + self.find_start_pattern_position(content))
        if self.end_pattern(): 
            self.set_end_extraction_position(content.find(self.end_pattern(), self.start_extraction_position() + 1) - 1)
            self.set_extracted_values(content[self.start_extraction_position():self.end_extraction_position()].strip())

    

