from __future__ import annotations # Allow referencing enclosing class in typings
from typing import List, Dict, Any
from abc import ABC

from ...model.event.stimulus import Stimulus
from ...model.event.feedback import Feedback


class CreateEventInput(ABC):

    @classmethod
    def to_json_object(cls, user_iri: str, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> Dict[str, Any]:
        return {
            'user': user_iri,
            'wasOriginatedBy': [stimulus.to_json_object() for stimulus in stimuli],
            'eventType': event_type_iri,
            'feedback': feedback.to_json_object()
        }


class UpdateEventInput(ABC):

    @classmethod
    def to_json_object(cls, user_iri: str, event_iri:str, stimuli: List[Stimulus], event_type_iri: str, feedback: Feedback) -> Dict[str, Any]:
        return {
            'user': user_iri,
            'event': event_iri,
            'wasOriginatedBy': [stimulus.to_json_object() for stimulus in stimuli],
            'eventType': event_type_iri,
            'feedback': feedback.to_json_object()
        }
