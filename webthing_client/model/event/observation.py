from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import Dict, Any, ClassVar

from webthing_client import utils


class Observation:

    type: ClassVar[str] = 'http://www.w3.org/ns/sosa/Observation'

    iri: ClassVar[None] = None


    result_time: datetime

    def __init__(self, result_time: datetime) -> None:
        self.result_time = result_time

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Observation:
        return cls(
            utils.parse_iso_time_format(json_object['resultTime'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resultTime': utils.to_iso_time_format(self.result_time)
        }

