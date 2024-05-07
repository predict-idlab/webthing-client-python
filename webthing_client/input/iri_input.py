from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Any
from abc import ABC


class IRIInput(ABC):

    @classmethod
    def to_json_object(cls, iri: str) -> Dict[str, Any]:
        return {
            '$iri': iri
        }
