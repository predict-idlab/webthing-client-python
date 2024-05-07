from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import Dict, Any, TypeVar, Generic

from webthing_client import utils


T = TypeVar('T', dict, list, str, int, float, None, bool)
class WebthingObservation(Generic[T]):

    timestamp: datetime

    value: T

    def __init__(self, timestamp: datetime, value: T) -> None:
        super().__init__()
        self.timestamp = timestamp
        self.value = value

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> WebthingObservation:
        return cls(
            utils.parse_iso_time_format(json_object['timestamp']),
            json_object['value']
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            'timestamp': utils.to_iso_time_format(self.timestamp),
            'value': self.value
        }
