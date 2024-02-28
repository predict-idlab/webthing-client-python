from __future__ import annotations # Allow referencing enclosing class in typings
from typing import *


class ObservableProperty:

    type: ClassVar[str] = 'http://www.w3.org/ns/sosa/ObservableProperty'


    iri: str

    name: Optional[str] = None

    realtime_datasource: Optional[str] = None

    historical_datasource: Optional[str] = None

    def __init__(self, iri: str, name: Optional[str], realtime_datasource: Optional[str], historical_datasource: Optional[str]) -> None:
        self.iri = iri
        self.name = name
        self.realtime_datasource = realtime_datasource
        self.historical_datasource = historical_datasource
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> ObservableProperty:
        return cls(
            json_object['$iri'],
            json_object.get('label'),
            json_object.get('realtimeDatasource'),
            json_object.get('historicalDatasource')
        )

    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'label': self.name,
            'realtimeDatasource': self.realtime_datasource,
            'historicalDatasource': self.historical_datasource
        }
