from __future__ import annotations # Allow referencing enclosing class in typings
from typing import Dict, Any, ClassVar, TypeVar, Generic
from abc import ABCMeta, abstractmethod

from ...ontology import WETHING_ONTOLOGY_PREFIX
from ...event.event import Event
from ...event.event_type import EventType


T = TypeVar('T')
class Operation(Generic[T], metaclass=ABCMeta):

    type: ClassVar[str]

    iri: ClassVar[None] = None


    resource_iri: str

    def __init__(self, resource_iri: str) -> None:
        super().__init__()
        self.resource_iri = resource_iri

    @classmethod
    def get_resource_type(cls) -> T:
        """Get the Type of the resource.

        Returns:
            T: Type of the resource.
        """
        # First get the base (Operation), then get T
        return get_args(cls.__orig_bases__[0])[0] # type: ignore

    @classmethod
    def is_resource_type(cls, type: Any) -> bool:
        """Returns true if the resource type matches. For example:
            operation.is_resource_type(Event)

        Args:
            type (Any): The type operation resource should be.

        Returns:
            bool: True if type.
        """
        return cls.get_resource_type() == type
    
    @classmethod
    def is_type(cls, type: Any) -> bool:
        """Returns true if the type of operation matches. For example:
            operation.is_type(CreateEventType)

        Args:
            type (Any): The type it should be.

        Returns:
            bool: True if type.
        """
        return cls == type

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> Operation[Any]:
        type: str = json_object['$class']
        if type == CreateEventOperation.type:
            return CreateEventOperation.from_json_object(json_object)
        elif type == UpdateEventOperation.type:
            return UpdateEventOperation.from_json_object(json_object)
        elif type == DeleteEventOperation.type:
            return DeleteEventOperation.from_json_object(json_object)
        elif type == UpdateEventTypeOperation.type:
            return UpdateEventTypeOperation.from_json_object(json_object)
        raise ValueError(f'No operation found for type <{type}>!')
    
    @abstractmethod
    def to_json_object(self) -> Dict[str, Any]:
        ...


CT = TypeVar('CT')
class CreateOperation(Operation[CT], Generic[CT], metaclass=ABCMeta):

    create: CT

    def __init__(self, resource_iri: str, create: CT) -> None:
        super().__init__(resource_iri)
        self.create = create


UT = TypeVar('UT')
class UpdateOperation(Operation[UT], metaclass=ABCMeta):

    update: UT

    def __init__(self, resource_iri: str, update: UT) -> None:
        super().__init__(resource_iri)
        self.update = update


DT = TypeVar('DT')
class DeleteOperation(Operation[DT], metaclass=ABCMeta):

    def __init__(self, resource_iri: str) -> None:
        super().__init__(resource_iri)


class CreateEventOperation(CreateOperation[Event]):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'CreateEventOperation'


    def __init__(self, create: Event) -> None:
        super().__init__(create.iri, create)

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> CreateEventOperation:
        return cls(
            Event.from_json_object_blank(json_object['create'], json_object['resource'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resource': self.resource_iri,
            'create': self.create.to_json_object_blank()
        }
    

class UpdateEventOperation(UpdateOperation[Event]):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'UpdateEventOperation'


    def __init__(self, update: Event) -> None:
        super().__init__(update.iri, update)

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> UpdateEventOperation:
        return cls(
            Event.from_json_object_blank(json_object['update'], json_object['resource'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resource': self.resource_iri,
            'update': self.update.to_json_object_blank()
        }
    

class DeleteEventOperation(DeleteOperation[Event]):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'DeleteEventOperation'


    def __init__(self, resource_iri: str) -> None:
        super().__init__(resource_iri)

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> DeleteEventOperation:
        return cls(json_object['resource'])
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resource': self.resource_iri,
        }


class UpdateEventTypeOperation(UpdateOperation[EventType]):

    type: ClassVar[str] = WETHING_ONTOLOGY_PREFIX + 'UpdateEventOperation'


    def __init__(self, update: EventType) -> None:
        super().__init__(update.iri, update)

    @classmethod
    def from_json_object(cls, json_object: Dict[str, Any]) -> UpdateEventTypeOperation:
        return cls(
            EventType.from_json_object_blank(json_object['update'], json_object['resource'])
        )
    
    def to_json_object(self) -> Dict[str, Any]:
        return {
            '$class': self.type,
            '$iri': self.iri,
            'resource': self.resource_iri,
            'update': self.update.to_json_object_blank()
        }
