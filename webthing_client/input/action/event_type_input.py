from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import Dict, Any
from abc import ABC

from ...model.event.feedback import Feedback


class UpdateEventTypeInput(ABC):

    @classmethod
    def to_json_object(cls, user_iri: str, event_type_iri: str, name: str, feedback: Feedback) -> Dict[str, Any]:
        return {
            'user': user_iri,
            'eventType': event_type_iri,
            'label': name,
            'feedback': feedback.to_json_object()
        }
