from __future__ import annotations # Allow referencing enclosing class in typings
from typing import *


class System:

    type: ClassVar[str] = 'http://www.w3.org/ns/ssn/System'


    iri: str

    name: Optional[str] = None

    child_iris: List[str] = []

    def __init__(self, iri: str, name: Optional[str], child_iris: List[str] ) -> None:
        self.iri = iri
        self.name = name
        self.child_iris = child_iris

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> System:
        return cls(
            json_object['$iri'],
            json_object.get('label'),
            json_object.get('hasSubSystem', [])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'hasSubSystem': self.child_iris
        }
