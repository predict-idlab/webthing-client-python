from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Optional, Any, ClassVar

from ..ontology import WETHING_ONTOLOGY_PREFIX


class User:

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'User'


    iri: str

    name: Optional[str] = None

    user_settings: UserSettings

    def __init__(self, iri: str, name: Optional[str], user_settings: UserSettings) -> None:
        self.iri = iri
        self.name = name
        self.user_settings = user_settings
    
    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> User:
        return cls(
            json_object['$iri'],
            json_object.get('label'),
            UserSettings.from_json_object(json_object['userSettings'])
        )

    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'userSettings': self.user_settings.to_json_object()
        }


class UserSettings:

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'UserSettings'

    iri: ClassVar[None] = None


    write_permission: bool

    def __init__(self, write_permission: bool) -> None:
        self.write_permission = write_permission

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> UserSettings:
        return cls(
            json_object['writePermission']
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'writePermission': self.write_permission
        }
