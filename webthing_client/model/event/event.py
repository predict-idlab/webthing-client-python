from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import *

from ..ontology import WETHING_ONTOLOGY_PREFIX
from .stimulus import Stimulus
from .feedback import Feedback
from webthing_client import utils


class Event:

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'Event'


    iri: str

    result_time: datetime

    stimuli: List[Stimulus]

    event_type_iri: str

    feedback: Feedback

    def __init__(self, iri: str, result_time: datetime, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> None:
        self.iri = iri
        self.result_time = result_time
        self.stimuli = stimuli
        self.event_type_iri = event_type_iri
        self.feedback = feedback

    @classmethod
    def from_json_object(cls, json_object: Optional[Dict[str, Any]]) -> Event:
        return cls(
            json_object['$iri'],
            utils.parse_iso_time_format(json_object['resultTime']),
            [Stimulus.from_json_object(stimulus_object) for stimulus_object in json_object.get('wasOriginatedBy', [])],
            json_object['eventType'],
            Feedback.from_json_object(json_object['feedback'])
        )
    
    @classmethod
    def from_json_object_blank(cls, json_object: Dict[str, Any], iri: str) -> Event:
        return cls(
            iri,
            utils.parse_iso_time_format(json_object['resultTime']),
            [Stimulus.from_json_object(stimulus_object) for stimulus_object in json_object.get('wasOriginatedBy', [])],
            json_object['eventType'],
            Feedback.from_json_object(json_object['feedback'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resultTime': utils.to_iso_time_format(self.result_time),
            'wasOriginatedBy': [stimulus.to_json_object() for stimulus in self.stimuli],
            'eventType': self.event_type_iri,
            'feedback': self.feedback.to_json_object()
        }
    
    def to_json_object_blank(self) -> Dict[str, Any]:
        return {
            '$class': WETHING_ONTOLOGY_PREFIX + 'BlankEvent',
            '$iri': None,
            'resultTime': utils.to_iso_time_format(self.result_time),
            'wasOriginatedBy': [stimulus.to_json_object() for stimulus in self.stimuli],
            'eventType': self.event_type_iri,
            'feedback': self.feedback.to_json_object()
        }
