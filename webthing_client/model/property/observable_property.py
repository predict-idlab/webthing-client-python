from __future__ import annotations # Allow referencing enclosing class in typings
from typing import *


class ObservableProperty:

    type: ClassVar[str] = 'http://www.w3.org/ns/sosa/ObservableProperty'


    iri: str

    name: Optional[str] = None

    def __init__(self, iri: str, name: Optional[str]) -> None:
        self.iri = iri
        self.name = name
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> ObservableProperty:
        return cls(
            json_object['$iri'],
            json_object.get('label')
        )
