from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Optional, Any, ClassVar

from .observation import Observation


class Stimulus:

    type: ClassVar[str]  = 'http://www.w3.org/ns/ssn/Stimulus'

    iri: ClassVar[None] = None


    property_iri: str

    from_observation: Observation

    to_observation: Observation

    def __init__(self, property_iri: str, from_observation: Observation, to_observation: Observation) -> None:
        self.property_iri = property_iri
        self.from_observation = from_observation
        self.to_observation = to_observation
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Stimulus:
        return cls(
            json_object['observedProperty'],
            Observation.from_json_object(json_object['fromObservation']),
            Observation.from_json_object(json_object['toObservation'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'observedProperty': self.property_iri,
            'fromObservation': self.from_observation.to_json_object(),
            'toObservation': self.to_observation.to_json_object()
        }