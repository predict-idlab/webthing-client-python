from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Any
from abc import ABC


class IRIUserInput(ABC):

    @classmethod
    def to_json_object(cls, user_iri: str, iri: str) -> Dict[str, Any]:
        return {
            '$iri' : iri,
            'user': user_iri
        }
