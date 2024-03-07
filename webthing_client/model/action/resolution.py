from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from enum import Enum
from typing import *

from webthing_client import utils
from ..ontology import WETHING_ONTOLOGY_PREFIX
from .request import Request
from .base import Base


class Resolution(Base):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'Resolution'


    verdicts: List[Verdict]

    action_iri: Optional[str] = None

    def __init__(self, iri: str, result_time: datetime, user_iri: str, verdicts: List[Verdict], action_iri: Optional[str]) -> None:
        super().__init__(iri, result_time, user_iri)
        self.verdicts = verdicts
        self.action_iri = action_iri
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Request:
        return cls(
            json_object['$iri'],
            utils.parse_iso_time_format(json_object['resultTime']),
            json_object['user'],
            [Verdict.from_json_object(verdict) for verdict in json_object['verdict']],
            json_object.get('action')
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resultTime': utils.to_iso_time_format(self.result_time),
            'verdict': [verdict.to_json_object() for verdict in self.verdicts],
            'action': self.action_iri
        }


class VerdictResultType(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIAL = "PARTIAL"


class Verdict():

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'Verdict'

    iri: ClassVar[str] = None


    verdict_result: VerdictResultType

    request: Request[Any]

    def __init__(self, verdict_result: VerdictResultType, request: Request[Any]) -> None:
        self.verdict_result = verdict_result
        self.request = request

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Request:
        return cls(
            json_object['verdictResult'],
            Request.from_json_object(json_object['request'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'request': self.request.to_json_object()
        }
