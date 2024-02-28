from __future__ import annotations # Allow referencing enclosing class in typings
from typing import *

from .feedback import Feedback


class EventType:

    type: ClassVar[str] = 'http://webthing.invalid/ontology/EventType'


    iri: str

    name: str

    feedback: Feedback

    type_feedback_iri: str

    event_feedback_iri: str

    def __init__(self, iri: str, name: str, feedback: str, type_feedback_iri: str, event_feedback_iri: str) -> None:
        self.iri = iri
        self.name = name
        self.feedback = feedback
        self.type_feedback_iri = type_feedback_iri
        self.event_feedback_iri = event_feedback_iri

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> EventType:
        return cls(
            json_object['$iri'],
            json_object['label'],
            Feedback.from_json_object(json_object['feedback']),
            json_object['typeFeedbackShape'],
            json_object['eventFeedbackShape']
        )
    
    @classmethod
    def from_json_object_blank(cls, json_object: Dict[str, Any], iri: str) -> EventType:
        return cls(
            iri,
            json_object['label'],
            Feedback.from_json_object(json_object['feedback']),
            json_object['typeFeedbackShape'],
            json_object['eventFeedbackShape']
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'label': self.name,
            'feedback': self.feedback.to_json_object(),
            'typeFeedbackShape': self.type_feedback_iri,
            'eventFeedbackShape': self.event_feedback_iri
        }
    
    def to_json_object_blank(self) -> Dict[str, Any]:
        return {
            '$class': 'http://webthing.invalid/ontology/BlankEventType',
            '$iri': None,
            'label': self.name,
            'feedback': self.feedback.to_json_object(),
            'typeFeedbackShape': self.type_feedback_iri,
            'eventFeedbackShape': self.event_feedback_iri
        }
