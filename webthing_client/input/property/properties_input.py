from __future__ import annotations # Allow referencing enclosing class in typings
from typing import List, Dict, Optional, Any
from abc import ABC


class PropertiesInput(ABC):

    @classmethod
    def to_json_object(cls, property_iris: Optional[List[str]]=None) -> Dict[str, Any]:
        return {
            'property': property_iris
        }
