from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import *

from webthing_client import utils
from .operation.operation import Operation
from .request import Request


T = TypeVar('T')
OT = TypeVar('OT', bound=Operation)
class Action(Request[T, OT], Generic[T, OT]):

    type: ClassVar[str] = 'http://webthing.invalid/ontology/Action'


    resolution_iri: Optional[str] = None

    def __init__(self, iri: str, result_time: datetime, user_iri: str, operation: Operation[T], resolution_iri: Optional[str]) -> None:
        super().__init__(iri, result_time, user_iri, operation)
        self.resolution_iri = resolution_iri
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Action:
        return cls(
            json_object['$iri'],
            utils.parse_iso_time_format(json_object['resultTime']),
            json_object['user'],
            Operation.from_json_object(json_object['operation']),
            json_object.get('resolution')
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resultTime': utils.to_iso_time_format(self.result_time),
            'user': self.user_iri,
            'operation': self.operation.to_json_object(),
            'resolution': self.resolution_iri
        }
