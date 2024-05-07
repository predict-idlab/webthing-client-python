from __future__ import annotations # Allow referencing enclosing class in typings
from typing import List, Dict, Optional, Any, ClassVar


class Sensor:

    type: ClassVar[str] = 'http://www.w3.org/ns/sosa/Sensor'


    iri: str

    name: Optional[str] = None

    property_iris: List[str] = []

    def __init__(self, iri: str, name: Optional[str], property_iris: List[str]) -> None:
        self.iri = iri
        self.name = name
        self.property_iris = property_iris

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Sensor:
        return cls(
            json_object['$iri'],
            json_object.get('label'),
            json_object.get('observes', [])
        )

    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'label': self.name,
            'observes': self.property_iris
        }