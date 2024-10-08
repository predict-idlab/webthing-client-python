from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import Dict, Any, ClassVar, TypeVar, Generic

from webthing_client import utils
from ..ontology import WETHING_ONTOLOGY_PREFIX
from .operation.operation import Operation
from .base import Base


T = TypeVar('T')
OT = TypeVar('OT', bound=Operation) # The operation generic type should match T type
class Request(Base, Generic[T, OT]):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'Request'


    operation: OT

    def __init__(self, iri: str, result_time: datetime, user_iri: str, operation: OT) -> None:
        super().__init__(iri, result_time, user_iri)
        self.operation = operation
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Request:
        return cls(
            json_object['$iri'],
            utils.parse_iso_time_format(json_object['resultTime']),
            json_object['user'],
            Operation.from_json_object(json_object['operation'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resultTime': utils.to_iso_time_format(self.result_time),
            'user': self.user_iri,
            'operation': self.operation.to_json_object()
        }