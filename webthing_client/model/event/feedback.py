from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Union, Optional, Any, ClassVar


class Feedback:

    iri: ClassVar[None] = None


    type: Optional[str] = None

    properties: Dict[str, Union[str, int, float, None, bool]] = {}

    def __init__(self, type: Optional[str], properties: Dict[str, Union[str, int, float, None, bool]]) -> None:
        self.type = type
        self.properties = properties

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Feedback:
        # Make copy of self and remove meta vars
        properties: Dict[str, Union[str, int, float, None, bool]] = dict(json_object)
        properties.pop('$class', None)
        properties.pop('$iri', None)
        return cls(
            json_object.get('$class'),
            properties
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        feedback_object: Dict[str, Union[str, int, float, None, bool]] = dict(self.properties)
        feedback_object['$class'] = self.type
        return feedback_object
