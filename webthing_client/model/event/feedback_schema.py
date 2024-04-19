from __future__ import annotations # Allow referencing enclosing class in typings
from typing import *

import jsonschema

from webthing_client.model.event.feedback import Feedback


class FeedbackSchema:

    type: Optional[str] = None

    schema: Dict[str, Any]

    def __init__(self, type: Optional[str], schema: Dict[str, Any]) -> None:
        self.type = type
        self.schema = schema

    def validate_feedback_object(self, feedback_object: Dict[str, Union[str, int, float, None, bool]]) -> None:
        """Validate JSON feedback object to Schema.

        Args:
            feedback_object (Dict[str, Union[str, int, float, None, bool]]): JSON feedback object | '{"test": "input"}'
        
        Raises:
            `jsonschema.exceptions.ValidationError`: if the instance is invalid
        """
        jsonschema.validate(feedback_object, self.schema)

    def valid_feedback_object(self, feedback_object: Dict[str, Union[str, int, float, None, bool]]) -> bool:
        """Validate JSON feedback object to Schema.

        Args:
            feedback_object (Dict[str, Union[str, int, float, None, bool]]): JSON feedback object | '{"test": "input"}'

        Returns:
            bool: If the feedback object is valid.
        """
        try:
            self.validate_feedback_object(feedback_object)
            return True
        except jsonschema.ValidationError:
            return False
        
    def feedback_from_feedback_object(self, feedback_object: Dict[str, Union[str, int, float, None, bool]]) -> Feedback:
        """Create Feedback from JSON feedback object on this Feedback Schema.

        Args:
            feedback_object (Dict[str, Union[str, int, float, None, bool]]): JSON feedback object | '{"test": "input"}'

        Returns:
            Feedback: Feedback linked to this Feedback Schema.
        """
        return Feedback(self.type, feedback_object)

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> FeedbackSchema:
        # Remove all meta properties
        properties: Dict[str, Any] = dict(json_object.get('properties'))
        properties.pop('$iri', None)
        properties.pop('$class', None)
        required: List[str] = []
        if 'required' in json_object:
            required = list(json_object.get('required'))
            required = list(set(required) - set(['$iri','$class']))
        schema: Dict[str, Any] = {
            '$schema': json_object['$schema'],
            'type': 'object',
            'properties': properties,
            'required': required
        }
        type: str = None
        if '$class' in json_object['properties']:
            type = json_object['properties']['$class']['const']
        return cls(type, schema)
