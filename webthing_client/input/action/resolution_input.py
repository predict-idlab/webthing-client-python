from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Optional, Any
from abc import ABC

from ...model.action.operation.operation import Operation
from ...model.action.resolution import VerdictResultType


class ResolutionInput(ABC):

    @classmethod
    def to_json_object(cls, user_iri: str, verdicts: Dict[str,VerdictResultType], operation: Optional[Operation[Any]]=None) -> Dict[str, Any]:
        return {
            'user': user_iri,
            'verdict': [VerdictInput.to_json_object(request_iri, result) for request_iri, result in verdicts.items()],
            'operation': operation.to_json_object() if operation is not None else None
        }

class VerdictInput(ABC):

    @classmethod
    def to_json_object(cls, request_iri: str, result: VerdictResultType) -> Dict[str, Any]:
        return {
            '$iri' : request_iri,
            'verdictResult': result.value
        }
