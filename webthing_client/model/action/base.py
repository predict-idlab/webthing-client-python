from __future__ import annotations # Allow referencing enclosing class in typings
from datetime import datetime
from typing import ClassVar
from abc import ABC


class Base(ABC):

    type: ClassVar[str]


    iri: str

    result_time: datetime

    user_iri: str

    def __init__(self, iri: str, result_time: datetime, user_iri: str) -> None:
        super().__init__()
        self.iri = iri
        self.result_time = result_time
        self.user_iri = user_iri
