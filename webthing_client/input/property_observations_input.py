from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import *
from abc import ABC

from webthing_client import utils


class PropertyObservationsInput(ABC):

    @classmethod
    def to_json_object(cls, property_iri: str, from_time: Optional[datetime]=None, to_time: Optional[datetime]=None) -> Dict[str, Any]:
        return {
            'property': property_iri,
            'from': utils.to_iso_time_format(from_time),
            'to': utils.to_iso_time_format(to_time)
        }
